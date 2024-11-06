import geopandas as gpd
import matplotlib.pyplot as plt

input_file = 'data_files/Madeira.gpkg'
output_file = 'data_files/geometry_output.txt'

try:
    gdf = gpd.read_file(input_file, layer='Culturas_Aveiro')
    
    # Extrair as coordenadas geográficas e salvar em um arquivo txt
    with open(output_file, 'w') as f:
        for geom in gdf['geometry']:
            f.write(f"{geom}\n")
    
    print(f"Coordenadas salvas em {output_file}")

except Exception as e:
    print(f"Erro ao ler o ficheiro: {e}")