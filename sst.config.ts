/// <reference path="./.sst/platform/config.d.ts" />

/**
 * Roux – AWS deployment via SST v3
 *
 * Stages:
 *   staging    – pre-production (sst deploy --stage staging)
 *   production – live environment (sst deploy --stage production)
 *
 * Prerequisites:
 *   - AWS CLI configured
 *   - Docker running (for image build)
 *   - npm install && npx sst deploy --stage staging
 */
export default $config({
  app(input) {
    return {
      name: "roux",
      removal: input?.stage === "production" ? "retain" : "remove",
      home: "aws",
      providers: {
        aws: {
          region: "eu-west-2",
        },
      },
    };
  },
  async run() {
    const stage = $app.stage;
    const isProd = stage === "production";

    const domain = isProd
      ? "app.roux.care"
      : `staging.roux.care`;

    // VPC and cluster
    const vpc = new sst.aws.Vpc("RouxVpc", {
      nat: isProd ? "managed" : "ec2",
    });

    const cluster = new sst.aws.Cluster("RouxCluster", { vpc });

    const franchiseDomain = isProd ? "roux.care" : "staging.roux.care";

    // PostgreSQL database
    const database = new sst.aws.Postgres("RouxDatabase", {
      vpc,
      scaling: isProd
        ? { min: "0.5 ACU", max: "4 ACU" }
        : { min: "0.5 ACU", max: "1 ACU" },
    });

    // S3 bucket for user uploads (logos, reports)
    const uploads = new sst.aws.Bucket("RouxUploads", {
      access: "cloudfront",
    });

    // Static assets bucket (collected Django staticfiles)
    const staticAssets = new sst.aws.Bucket("RouxStatic", {
      access: "cloudfront",
    });

    // Secrets – set via: sst secret set SecretKey <value> --stage <stage>
    const secretKey = new sst.Secret("SecretKey");
    const stripeSecretKey = new sst.Secret("StripeSecretKey");
    const stripeWebhookSecret = new sst.Secret("StripeWebhookSecret");
    const xeroClientSecret = new sst.Secret("XeroClientSecret");

    const web = new sst.aws.Service("RouxWeb", {
      cluster,
      cpu: isProd ? "0.5 vCPU" : "0.25 vCPU",
      memory: isProd ? "1 GB" : "0.5 GB",
      scaling: isProd
        ? { min: 2, max: 6 }
        : { min: 1, max: 2 },
      link: [database, uploads, staticAssets],
      loadBalancer: {
        domain: {
          name: domain,
          dns: false,
        },
        ports: [
          { listen: "80/http", forward: "8000/http" },
          { listen: "443/https", forward: "8000/http" },
        ],
        health: {
          "8000/http": {
            path: "/",
            interval: "30 seconds",
            timeout: "5 seconds",
          },
        },
      },
      environment: {
        DJANGO_SETTINGS_MODULE: "config.settings",
        DEBUG: isProd ? "False" : "True",
        ALLOWED_HOSTS: `.${franchiseDomain},${domain}`,
        SECRET_KEY: secretKey.value,
        STRIPE_SECRET_KEY: stripeSecretKey.value,
        STRIPE_WEBHOOK_SECRET: stripeWebhookSecret.value,
        XERO_CLIENT_SECRET: xeroClientSecret.value,
        DATABASE_URL: $interpolate`postgresql://${database.username}:${database.password}@${database.host}:${database.port}/${database.database}`,
        FRANCHISE_DATABASE_URL_TEMPLATE: $interpolate`postgresql://${database.username}:${database.password}@${database.host}:${database.port}/{db_name}`,
        FRANCHISE_BASE_DOMAIN: franchiseDomain,
        PLATFORM_ADMIN_EMAIL: `partnerships@${franchiseDomain}`,
        DEFAULT_ORGANISATION_SLUG: "demo-club",
        EMAIL_BACKEND: "django.core.mail.backends.smtp.EmailBackend",
        DEFAULT_FROM_EMAIL: `noreply@${domain}`,
        AWS_STORAGE_BUCKET_NAME: uploads.name,
        AWS_S3_REGION_NAME: "eu-west-2",
        XERO_REDIRECT_URI: `https://${domain}/dashboard/finance/xero/callback/`,
      },
      dev: {
        command: "python manage.py runserver 0.0.0.0:8000",
        url: "http://localhost:8000",
      },
      image: {
        context: ".",
        dockerfile: "Dockerfile",
      },
    });

    return {
      web: web.url,
      database: database.host,
      uploads: uploads.name,
      staticAssets: staticAssets.name,
      stage,
    };
  },
});
