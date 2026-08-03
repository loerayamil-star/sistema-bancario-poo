# Sistema Bancario POO

Simulador de un sistema bancario simple escrito en Python puro, usando
programación orientada a objetos. Permite crear clientes, abrir cuentas,
depositar, retirar, transferir entre cuentas y persistir todo el estado
en un archivo JSON.

Es un proyecto de práctica/aprendizaje: no está pensado para manejar
dinero real ni para exponerse como servicio en producción.

## Qué hace

- Crea **clientes** que pueden tener una o varias **cuentas**.
- Cada cuenta soporta depósitos, retiros y transferencias, con
  validaciones de monto y saldo.
- Cada cuenta protege su contraseña con un hash (no se guarda en texto
  plano) y bloquea las operaciones después de varios intentos fallidos.
- Registra un historial de transacciones (depósito, retiro,
  transferencia) con fecha y hora en UTC.
- Persiste todo el sistema (clientes + cuentas) en un archivo JSON y
  puede recargarlo íntegramente en una sesión nueva.
- Usa excepciones propias para cada tipo de error de negocio, en vez de
  errores genéricos.

## Requisitos

- Python 3.9 o superior (usa `datetime.timezone.utc` y f-strings-safe
  syntax; no requiere ninguna librería externa).
- No hay dependencias de terceros: solo usa la librería estándar
  (`datetime`, `hashlib`, `json`).

## Instalación

```bash
git clone <url-del-repositorio>
cd sistema-bancario-poo
```

No hay `requirements.txt` ni entorno virtual que configurar: todo el
proyecto vive en `sistema_bancario.py` y solo usa la librería estándar
de Python.

## Cómo correrlo

El archivo `sistema_bancario.py` es un módulo de clases, no un script
con `if __name__ == "__main__":`. Para usarlo, impórtalo desde tu propio
script o desde una sesión interactiva:

```bash
python3
```

```python
from sistema_bancario import SistemaBancario, Cliente, Cuenta

banco = SistemaBancario()
cliente = Cliente("Yamil")
cuenta = Cuenta("1234567890", "1234")

banco.agregar_cliente(cliente)
banco.agregar_cuenta(cliente, cuenta)

cuenta.depositar(1000)
banco.guardar_json()  # crea/actualiza datos_banco.json
```

## Arquitectura

El proyecto tiene tres clases principales y siete excepciones propias,
todas en `sistema_bancario.py`.

### `Cuenta`

Representa una cuenta bancaria individual.

- **Atributos**: `numero_cuenta`, `saldo`, `contrasena` (hash SHA-256,
  nunca el valor original), `historial_transacciones`,
  `intentos_fallidos`.
- **Operaciones**: `depositar`, `retirar`, `transferir` (mueve saldo
  entre dos objetos `Cuenta` y registra la transacción en ambas puntas
  implícitamente vía `retirar`/`depositar`).
- **Validaciones**: `validar_monto` (rechaza montos no numéricos o
  ≤ 0) y `validar_saldo` (rechaza retiros sin fondos y bloquea la
  cuenta tras 5 intentos fallidos).
- **Autenticación**: `verificar_contrasena` compara el hash de la
  contraseña ingresada contra el hash guardado, sin exponer nunca la
  contraseña real.
- **Serialización**: `a_diccionario` / `desde_diccionario` convierten
  la cuenta (incluido el historial, con fechas ISO 8601) a/desde un
  `dict` apto para JSON.

### `Cliente`

Agrupa varias cuentas bajo un nombre.

- **Atributos**: `nombre`, `cuentas` (dict `numero_cuenta -> Cuenta`).
- `agregar_cuenta` / `consultar_cuentas` (esta última devuelve una
  copia del dict, para que quien consulta no pueda mutar el estado
  interno del cliente).
- `a_diccionario` / `desde_diccionario` para persistencia.

### `SistemaBancario`

Orquesta todo: es el punto de entrada para operar con clientes y
cuentas, y para guardar/cargar el estado completo.

- **Atributos**: `base_clientes` (nombre -> `Cliente`), `base_sistema`
  (numero_cuenta -> `Cuenta`, índice plano para búsquedas rápidas por
  cuenta sin recorrer clientes).
- `agregar_cliente`, `agregar_cuenta`, `buscar_cliente`,
  `buscar_cuenta`: altas y búsquedas, con excepciones específicas si no
  existen.
- `realizar_transferencia(numero_origen, numero_destino, monto)`:
  busca ambas cuentas por número y delega en `Cuenta.transferir`.
- `guardar_json` / `cargar_json`: serializan/deserializan **todo** el
  sistema (clientes y el índice de cuentas) a un archivo JSON
  (`datos_banco.json` por defecto).

### Excepciones propias

`ContrasenaInvalidaError`, `ContrasenaIncorrectaError`,
`ClienteNoEncontradoError`, `CuentaNoEncontradaError`,
`SaldoInsuficienteError`, `IntentosExcedidosError`,
`MontoInvalidoError`.

Todas heredan directamente de `Exception`.

## 🧪 Cómo correr las pruebas

Este proyecto aún no tiene suite de tests automatizada — es una mejora 
planeada para v4, junto con la interfaz web.

## Ejemplos de uso

### Crear cliente, cuenta, depositar y retirar

```python
from sistema_bancario import SistemaBancario, Cliente, Cuenta

banco = SistemaBancario()

cliente = Cliente("Yamil")
banco.agregar_cliente(cliente)

cuenta = Cuenta("1234567890", "1234")
banco.agregar_cuenta(cliente, cuenta)

cuenta.depositar(500)
cuenta.retirar(200)

print(cuenta.saldo)  # 300
```

### Transferencia entre cuentas

```python
cuenta_destino = Cuenta("0987654321", "5678")
banco.agregar_cuenta(cliente, cuenta_destino)

banco.realizar_transferencia("1234567890", "0987654321", 100)
```

### Manejo de errores específicos

```python
from sistema_bancario import SaldoInsuficienteError

try:
    cuenta.retirar(10_000_000)
except SaldoInsuficienteError as error:
    print(f"No se pudo retirar: {error}")
```

### Autenticación

```python
from sistema_bancario import ContrasenaIncorrectaError

try:
    cuenta.verificar_contrasena("0000")
except ContrasenaIncorrectaError as error:
    print(error)
```

### Persistir y recargar el sistema completo

```python
banco.guardar_json("datos_banco.json")

# ... en otra sesión / reinicio del programa ...
banco_restaurado = SistemaBancario.cargar_json("datos_banco.json")
cuenta_recuperada = banco_restaurado.buscar_cuenta("1234567890")
```

## Decisiones de diseño

**Hash de contraseña (SHA-256) en vez de texto plano.**
La contraseña nunca se guarda ni se compara en texto plano: se guarda
su hash (`Cuenta.__init__`) y `verificar_contrasena` compara hashes, no
valores originales. Esto evita que quien lea `datos_banco.json`
directamente (o el propio código) tenga acceso a la contraseña real.

> Nota honesta: SHA-256 es un hash rápido y sin *salt*, pensado para
> integridad de datos, no para almacenamiento de contraseñas. Para un
> sistema real se preferiría un KDF lento y salteado (bcrypt, scrypt o
> Argon2). Aquí se usa SHA-256 por simplicidad, dado que es un proyecto
> educativo sin dependencias externas.

**Excepciones personalizadas en vez de errores genéricos.**
Cada situación de negocio (saldo insuficiente, cuenta no encontrada,
contraseña incorrecta, monto inválido, etc.) tiene su propia clase de
excepción. Esto permite que quien use `SistemaBancario`/`Cuenta` capture
exactamente el error que le interesa (`except SaldoInsuficienteError`)
sin tener que parsear mensajes de texto ni capturar `Exception` a
ciegas, que ocultaría bugs reales junto con los errores esperados.

**Bloqueo tras intentos fallidos (`intentos_fallidos` /
`IntentosExcedidosError`).**
Tanto los retiros sin fondos como las contraseñas incorrectas suman al
mismo contador. Al llegar a 5, la cuenta deja de aceptar operaciones.
Es una defensa simple contra fuerza bruta / abuso, aunque en este
proyecto no hay forma de resetear el contador (se dejaría como mejora
futura).

**Copias defensivas en consultas (`consultar_historial`,
`consultar_cuentas`).**
Ambos métodos devuelven `.copy()` de sus estructuras internas, no la
referencia original. Así, código externo que reciba el resultado no
puede mutar por accidente el historial de transacciones o el diccionario
de cuentas del cliente.

**Persistencia en JSON plano, sin base de datos.**
Todo el estado del sistema se puede volcar a un único archivo JSON
(`a_diccionario` / `guardar_json`) y reconstruirse por completo
(`desde_diccionario` / `cargar_json`). Es la opción más simple posible
para un proyecto sin dependencias externas; no está pensada para
concurrencia ni para volúmenes grandes de datos.

## Sobre el archivo `.env`

Este proyecto **no necesita** un archivo `.env` y por eso no se incluye
ninguno.

Un `.env` sirve para mantener fuera del control de versiones
credenciales o configuración sensible que el código necesita en tiempo
de ejecución: claves de API de terceros, cadenas de conexión a bases de
datos, tokens de servicios externos, *secrets* para firmar JWT, etc.

Este proyecto no llama a ningún servicio externo, no usa una base de
datos con credenciales, ni tiene claves de API. Su única "credencial"
es la contraseña de cada cuenta bancaria, y esa vive dentro de los
datos del propio dominio (hasheada, dentro de `datos_banco.json`), no
como un secreto de configuración del sistema. Por eso no aplica un
`.env`.

Si en el futuro el proyecto agregara, por ejemplo, un backend con base
de datos externa, un servicio de envío de correos, o claves para firmar
tokens de sesión, ahí sí tendría sentido introducir un `.env` (y
agregarlo a `.gitignore`) para no commitear esos secretos al
repositorio.

## Roadmap

- **v4 — Interfaz web (HTML/CSS/JS):** la siguiente versión planea
  agregar una interfaz web que consuma la lógica de `SistemaBancario`,
  permitiendo operar el banco (crear cuentas, depositar, retirar,
  transferir, ver historial) desde el navegador en vez de la consola
  interactiva de Python.
