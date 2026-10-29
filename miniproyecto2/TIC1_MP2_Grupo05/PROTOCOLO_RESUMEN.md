# Resumen del protocolo

El host central mantiene el estado global del juego. La Raspberry Pi del grupo sólo
necesita conocer los eventos y parámetros que modifican su comportamiento local.

## Mensajes enviados por el jugador

- `Join`
- `StageReady`
- `Result`
- `Recover`

## Mensajes recibidos desde el host central

- `Accepted`
- `StageStart`
- `FinalStart`
- `StageReadyAccepted`
- `StageActive`
- `Assign`
- `Sabotage`
- `ResultAccepted`
- `RecoverAccepted`
- `Eliminated`
- `GameOver`
- `Error`

Durante las pruebas también puede recibirse `TestStageComplete`.

## Información necesaria

Un `Assign` entrega `GameID` y `Attempt` para identificar el minijuego solicitado.

Un `Sabotage` entrega `Effect` y `Value` para aplicar el efecto correspondiente.

`FinalStart` puede entregar `ReactionPresses`, porque este valor indica cuántas
pulsaciones debe detectar el cliente para generar un `Recover`.

Los mensajes `StageReadyAccepted`, `ResultAccepted` y `RecoverAccepted` funcionan
principalmente como confirmaciones y se relacionan con el mensaje original mediante
`ReplyTo`.

## Información administrada exclusivamente por el host

El cliente no necesita conocer ni almacenar:

- vida del jugador;
- vida del jefe;
- postura global;
- cantidad de vida recuperada por `Recover`;
- incremento de postura por `Recover`;
- valor máximo de postura;
- daño aplicado al jefe;
- contadores internos de sabotajes;
- estado interno de invulnerabilidad;
- información interna de transición entre etapas.

El host central calcula estas variables y envía únicamente los eventos que afectan al
jugador, por ejemplo `Eliminated` o `GameOver`.
