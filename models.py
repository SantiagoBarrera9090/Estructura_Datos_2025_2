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

    def __init__(  # función que se ejecuta cuando creamos un nuevo registro de cliente
        self,  # referencia a este objeto que estamos creando
        customer_id,  # el identificador único del cliente
        first_name,  # primer nombre de la persona
        last_name,  # apellido de la persona
        company,  # nombre de la empresa donde trabaja
        city,  # ciudad donde vive el cliente
        country,  # país de residencia del cliente
        email,  # dirección de correo electrónico
        subscription_date,  # fecha cuando se suscribió (puede venir como texto)
        website,  # página web personal o empresarial
    ):
        # tomamos cada dato que nos pasaron y lo guardamos en este objeto
        self.customer_id = customer_id  # guardamos el ID único que identifica a este cliente
        self.first_name = first_name  # guardamos el primer nombre para poder usarlo después
        self.last_name = last_name  # guardamos el apellido para identificación completa
        self.company = company  # guardamos dónde trabaja para información de contacto
        self.city = city  # guardamos la ciudad para saber su ubicación
        self.country = country  # guardamos el país para análisis geográfico
        self.email = email  # guardamos el email para futuras comunicaciones

        # la fecha necesita procesamiento especial porque puede venir en muchos formatos diferentes
        self.subscription_date = self._parse_date(subscription_date)  # convertimos el texto a fecha real

        self.website = website  # guardamos la página web si la tiene

    def _parse_date(self, value):  # función privada para convertir diferentes formatos de fecha
        """Esta función convierte texto en fecha real.
        
        A veces las fechas vienen como texto y necesitamos convertirlas a fechas de verdad
        para poder compararlas y ordenarlas correctamente.
        """
        if value is None:  # si no nos pasaron ninguna fecha
            return None  # devolvemos None para indicar que no hay fecha
        if isinstance(value, date):  # si ya es una fecha de Python
            return value  # la devolvemos tal como está
        s = str(value).strip()  # convertimos a texto y quitamos espacios en blanco
        if not s:  # si después de limpiar queda vacío
            return None  # no hay fecha válida
        # probamos diferentes formatos comunes de fecha hasta encontrar uno que funcione
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):  # formatos: año-mes-día, día/mes/año, año/mes/día
            try:  # intentamos convertir con este formato
                return datetime.strptime(s, fmt).date()  # si funciona, devolvemos la fecha
            except Exception:  # si este formato no funciona
                continue  # probamos el siguiente formato
        # si ningún formato funcionó, no pudimos convertir la fecha
        return None  # devolvemos None para indicar fecha inválida

    def __str__(self):  # función que convierte este registro en texto legible
        # preparamos la fecha para mostrar: si existe la convertimos a formato estándar, si no, texto vacío
        date_str = self.subscription_date.isoformat() if self.subscription_date else ""  # formato YYYY-MM-DD o vacío
        # construimos una línea de texto con todos los datos separados por guiones para fácil lectura
        return (  # devolvemos una cadena con todos los campos del cliente
            f"{self.customer_id} - {self.first_name} - {self.last_name} - {self.company} - "  # ID, nombre, apellido, empresa
            f"{self.city} - {self.country} - {self.email} - {date_str} - {self.website}"  # ciudad, país, email, fecha, web
        )  # el resultado es una línea completa con toda la información del cliente
