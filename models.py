from datetime import datetime, date


class Record:
    """
    Registro de cliente.

    Nota (comentario estilo estudiante colombiano): este objeto representa una fila del CSV.
    No es nada del otro mundo, pero nos permite acceder a cada campo por atributo.
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
        # Asignacion directa, sin vueltas.
        self.customer_id = customer_id
        self.first_name = first_name
        self.last_name = last_name
        self.company = company
        self.city = city
        self.country = country
        self.email = email

        # Fecha: intento parsear de forma tolerante.
        self.subscription_date = self._parse_date(subscription_date)

        self.website = website

    def _parse_date(self, value):
        """Intenta convertir cadenas a date; si falla devuelve None.

        Comentario colombiano: 'si la fecha viene medio rara, no se rompera todo el programa'.
        """
        if value is None:
            return None
        if isinstance(value, date):
            return value
        s = str(value).strip()
        if not s:
            return None
        # intentos comunes
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(s, fmt).date()
            except Exception:
                continue
        # si no se pudo, devolvemos None en vez de crash
        return None

    def __str__(self):
        # imprimimos con ' - ' tal como pidieron, sin drama
        date_str = self.subscription_date.isoformat() if self.subscription_date else ""
        return (
            f"{self.customer_id} - {self.first_name} - {self.last_name} - {self.company} - "
            f"{self.city} - {self.country} - {self.email} - {date_str} - {self.website}"
        )
