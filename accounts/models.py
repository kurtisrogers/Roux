from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMIN = "super_admin", "Super Admin"
        FRANCHISE_ADMIN = "franchise_admin", "Franchise Admin"
        ORG_ADMIN = "org_admin", "Organisation Admin"
        SITE_MANAGER = "site_manager", "Site Manager"
        STAFF = "staff", "Staff"
        FINANCE = "finance", "Finance"
        PARENT = "parent", "Parent / Guardian"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PARENT,
    )
    phone = models.CharField(max_length=20, blank=True)
    organisation = models.ForeignKey(
        "organisations.Organisation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )
    site = models.ForeignKey(
        "organisations.Site",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="staff",
    )

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self) -> str:
        return self.get_full_name() or self.username

    @property
    def is_staff_role(self) -> bool:
        return self.role in {
            self.Role.SUPER_ADMIN,
            self.Role.FRANCHISE_ADMIN,
            self.Role.ORG_ADMIN,
            self.Role.SITE_MANAGER,
            self.Role.STAFF,
            self.Role.FINANCE,
        }

    @property
    def is_franchise_admin(self) -> bool:
        return self.role in {self.Role.SUPER_ADMIN, self.Role.FRANCHISE_ADMIN}

    @property
    def is_dashboard_user(self) -> bool:
        return self.role != self.Role.PARENT

    def has_org_access(self, organisation) -> bool:
        if self.role == self.Role.SUPER_ADMIN:
            return True
        if self.role == self.Role.FRANCHISE_ADMIN:
            return True
        return self.organisation_id == organisation.id
