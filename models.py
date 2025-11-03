from datetime import datetime, date


class Record:
    """
    Registro de cliente.

    Representa una fila del CSV con los campos utilizados por el programa.
    Proporciona acceso directo a cada campo como atributos.
    """

    __slots__ = (
        "customer_id",
        "first_name",
        "last_name",
        "company",
        "city",
        "country",
        "email",
        "subscription_date",
        "website",
    )

    def __init__(
        self,
        customer_id,
        first_name,
        last_name,
        company,
        city,
        country,
        email,
        subscription_date,
        website,
    ):
        # Asignación directa de atributos.
        self.customer_id = customer_id
        self.first_name = first_name
        self.last_name = last_name
        self.company = company
        self.city = city
        self.country = country
        self.email = email

        # Fecha: parseo tolerante.
        self.subscription_date = self._parse_date(subscription_date)

        self.website = website

    def _parse_date(self, value):
        """Intenta convertir cadenas a date; si falla devuelve None.

        Si la fecha no es válida, se devuelve None en lugar de generar una excepción.
        """
        if value is None:
            return None
        if isinstance(value, date):
            return value
        s = str(value).strip()
        if not s:
            return None
        # Formatos comunes intentados
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(s, fmt).date()
            except Exception:
                continue
        # si no se pudo parsear, devolvemos None
        return None

    def __str__(self):
        # Formatea el registro con ' - ' entre campos
        date_str = self.subscription_date.isoformat() if self.subscription_date else ""
        return (
            f"{self.customer_id} - {self.first_name} - {self.last_name} - {self.company} - "
            f"{self.city} - {self.country} - {self.email} - {date_str} - {self.website}"
        )
