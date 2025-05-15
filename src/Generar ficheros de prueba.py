import pandas as pd
import numpy as np
import random
import os

# Ruta al archivo original
archivo_original = "Incarlopsa_Asignacion_v7_SM37 (2).xlsx"

# Leer las hojas relevantes
df_demanda = pd.read_excel(archivo_original, sheet_name="DemandaMataderos")
df_oferta = pd.read_excel(archivo_original, sheet_name="OfertaProveedores")

# Función para modificar solo los valores numéricos con una variación del ±10%
def modificar_numericos(df):
    df_mod = df.copy()
    for col in df.columns[2:]:  # Asume que las 2 primeras columnas son de identificación
        df_mod[col] = df[col].apply(
            lambda x: max(0, int(x * random.uniform(0.9, 1.1))) if isinstance(x, (int, float)) and not pd.isna(x) else x
        )
    return df_mod

# Crear múltiples versiones del archivo
for i in range(1, 7):
    df_demanda_mod = modificar_numericos(df_demanda)
    df_oferta_mod = modificar_numericos(df_oferta)

    nuevo_nombre = f"Incarlopsa_Asignacion_v7_SM37_version_{i}.xlsx"
    with pd.ExcelWriter(nuevo_nombre, engine='openpyxl') as writer:
        df_demanda_mod.to_excel(writer, sheet_name="DemandaMataderos", index=False)
        df_oferta_mod.to_excel(writer, sheet_name="OfertaProveedores", index=False)

    print(f"✅ Generado: {nuevo_nombre}")
