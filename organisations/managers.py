from django.db import models


class OrganisationScopedQuerySet(models.QuerySet):
    def for_organisation(self, organisation):
        if organisation is None:
            return self
        return self.filter(organisation=organisation)


class OrganisationScopedManager(models.Manager):
    def get_queryset(self):
        return OrganisationScopedQuerySet(self.model, using=self._db)

    def for_organisation(self, organisation):
        return self.get_queryset().for_organisation(organisation)
