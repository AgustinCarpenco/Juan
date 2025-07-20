import pandas as pd
import os

def cargar_excel(path):
    """Carga un archivo Excel y retorna un DataFrame. Maneja errores de carga."""
    if not os.path.exists(path):
        print(f"[ERROR] El archivo no existe: {path}")
        return None
    try:
        df = pd.read_excel(path)
        print(f"[INFO] Archivo cargado correctamente: {path}")
        return df
    except Exception as e:
        print(f"[ERROR] Fallo al cargar el archivo: {e}")
        return None

def inspeccion_inicial(df):
    """Muestra información básica del DataFrame: shape, columnas, tipos, nulos, duplicados, head y tail."""
    if df is None:
        print("[ERROR] DataFrame vacío o no cargado.")
        return
    print("\n[INFO] Dimensiones:", df.shape)
    print("\n[INFO] Columnas:", df.columns.tolist())
    print("\n[INFO] Tipos de datos:")
    print(df.dtypes)
    print("\n[INFO] Valores nulos por columna:")
    print(df.isnull().sum())
    print("\n[INFO] Duplicados:", df.duplicated().sum())
    print("\n[INFO] Primeras filas:")
    print(df.head())
    print("\n[INFO] Últimas filas:")
    print(df.tail())
    print("\n[INFO] Estadísticas descriptivas:")
    print(df.describe(include='all'))

if __name__ == "__main__":
    ruta = "data/1ra evaluación.xlsx"
    df = cargar_excel(ruta)
    inspeccion_inicial(df)
