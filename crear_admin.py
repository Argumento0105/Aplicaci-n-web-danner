from getpass import getpass
from app import create_app
from app.extensions import db
from app.models.usuario import Usuario

app = create_app()

with app.app_context():

    print("\n===================================")
    print("       CREAR ADMINISTRADOR")
    print("             ANUNCIA")
    print("===================================\n")

    nombre = input("Nombre: ").strip()
    apellido = input("Apellido: ").strip()
    correo = input("Correo electrónico: ").strip().lower()
    password = getpass("Contraseña: ")
    confirmar = getpass("Confirmar contraseña: ")

    if not nombre or not apellido or not correo:
        print("\nTodos los campos son obligatorios.")
        raise SystemExit(1)

    if len(password) < 8:
        print("\nLa contraseña debe tener al menos 8 caracteres.")
        raise SystemExit(1)

    if password != confirmar:
        print("\nLas contraseñas no coinciden.")
        raise SystemExit(1)

    existente = db.session.scalar(
        db.select(Usuario).filter_by(correo=correo)
    )

    if existente:
        print("\nEste correo ya está registrado.")
        raise SystemExit(1)

    administrador = Usuario(
        nombre=nombre,
        apellido=apellido,
        correo=correo,
        rol="admin",
        estado=True
    )

    administrador.establecer_password(password)

    db.session.add(administrador)
    db.session.commit()

    print("\nAdministrador creado correctamente.")
    print("Correo:", correo)
    print("Rol: ADMIN")
    print("\nYa puedes ingresar a ANUNCIA.")