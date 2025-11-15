from datetime import datetime, date


class Record:
    """
    Esta clase representa la información de un cliente individual.
    
    Cada Record contiene todos los datos de una persona que está en nuestra base de datos.
    Es como una ficha con toda la información personal y de contacto.
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
        # Guardamos toda la información del cliente en variables fáciles de usar
        self.customer_id = customer_id  # el número único que identifica a este cliente
        self.first_name = first_name  # el nombre de pila de la persona
        self.last_name = last_name  # el apellido de la persona
        self.company = company  # la empresa donde trabaja
        self.city = city  # la ciudad donde vive
        self.country = country  # el país donde vive
        self.email = email  # su dirección de correo electrónico

        # La fecha necesita un tratamiento especial porque puede venir en diferentes formatos
        self.subscription_date = self._parse_date(subscription_date)

        self.website = website  # su página web personal o de la empresa

    def _parse_date(self, value):
        """Esta función convierte texto en fecha real.
        
        A veces las fechas vienen como texto y necesitamos convertirlas a fechas de verdad
        para poder compararlas y ordenarlas correctamente.
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
