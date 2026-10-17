## Nota tecnica

### Responsabilidades

- contracts.py: es el contrato sirve para validar los campos, tipos y rangos de entrada, la categoría, confianza y versiones de salida.
- preprocess.py: crea los vectores que procesa el modelo a partir de la tabla de datos con las 11 variables.
- inference.py: carga el modelo, comprueba la compatibilidad
  y ejecuta la predicción.
- predict_file.py: da los resultados de la prediccion.

### Decisión 1: validar antes de predecir

Se revisa en preprocesado si los datos entran dentro de los rangos establecidos y si cumple el contrato antes de validar.

### Decisión 2: centralizar el orden de las características

Defino FEATURE_NAMES en preprocess.py y construyo el vector
siguiendo ese orden, independientemente del orden del CSV.
Al cargar el artefacto, compruebo que feature_names coincide. 
De esa forma impido que tome los valores de una variable para otra si el orden esta cambiado.