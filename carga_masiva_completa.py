import os
import django
import csv
import re
import decimal
import datetime
from django.db import IntegrityError, transaction

# Configura el entorno de Django para poder usar los modelos
# ¡CORREGIDO! Usa el nombre de tu proyecto: 'gestor_negocios.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestor_negocios.settings')
django.setup()

from productos.models import (
    Producto, VariacionProducto, Categoria, Subcategoria, Marca, 
    Atributo, ValorAtributo, MedidasProducto, Proveedor, Venta, Compra
)

def parsear_medidas(texto_medidas):
    """
    Función para extraer medidas de un texto.
    Se adapta a tu formato de datos.
    """
    medidas = {}
    patrones = {
        'longitud': r'Longitud del pie\s*=\s*(\d+\.?\d*)\s*cm',
        'anchura': r'Ancho Metatarsal\s*=\s*(\d+\.?\d*)\s*cm',
        'alto': r'Altura de la caña\s*=\s*(\d+\.?\d*)\s*cm',
        'peso': r'peso:\s*(\d+\.?\d*)'
    }

    for key, patron in patrones.items():
        match = re.search(patron, texto_medidas, re.IGNORECASE)
        if match:
            try:
                # Reemplaza coma por punto para el DecimalField
                medidas[key] = decimal.Decimal(match.group(1).replace(',', '.'))
            except (ValueError, decimal.InvalidOperation):
                medidas[key] = decimal.Decimal('0.00')
    return medidas

def importar_articulos_desde_csv(nombre_archivo):
    print(f"Iniciando la importación desde '{nombre_archivo}'...")
    
    # Diccionarios para almacenar objetos en caché y evitar consultas repetidas
    categorias_cache = {}
    subcategorias_cache = {}
    marcas_cache = {}
    proveedores_cache = {}
    atributos_cache = {}
    
    # Cache para ValorAtributo para evitar duplicados. La clave es (nombre_atributo, valor)
    valores_atributos_cache = {} 

    total_filas_procesadas = 0
    
    # Listas para bulk_create (solo para modelos sin relaciones Many-to-Many)
    productos_a_crear = []
    variaciones_a_crear = []
    
    # Listas temporales para dependientes, que serán filtradas más adelante
    medidas_temp = []
    compras_temp = []
    ventas_temp = []
    
    # Lista para gestionar las relaciones Many-to-Many
    variaciones_con_atributos = []

    with transaction.atomic():
        try:
            # CORREGIDO: encoding='latin-1' para caracteres especiales y el nombre del archivo es 'datos.csv'
            with open(nombre_archivo, mode='r', newline='', encoding='latin-1') as file:
                # CORREGIDO: Usamos la variable 'file', NO 'archivo_csv'
                lector = csv.DictReader(file)
                
                for i, fila in enumerate(lector, 1):
                    total_filas_procesadas = i
                    
                    # Salta las filas completamente vacías
                    if not any(fila.values()):
                        continue
                    
                    nombre_producto = fila.get('Nombre Producto', '').strip()
                    
                    # CORRECCIÓN CLAVE: Si el nombre del producto es N/A o vacío, lo omitimos para evitar el error de FK.
                    if not nombre_producto or nombre_producto == 'N/A':
                         print(f"⚠️ Advertencia: Fila {i} omitida: El 'Nombre Producto' está vacío o es 'N/A'.")
                         continue

                    print(f"Procesando fila {i}: {nombre_producto}")

                    # --- 1. Obtener o crear modelos relacionados (en caché) ---
                    # Categoria y Subcategoria
                    cat_sub_str = fila.get('Categoria', '').strip()
                    # Intenta dividir la categoría
                    if cat_sub_subdivision := re.match(r'(\d+\.\d+)\s*(.*)', cat_sub_str):
                        categoria_nombre = cat_sub_subdivision.group(1).split('.')[0]
                        subcategoria_nombre = cat_sub_subdivision.group(2).strip()
                        if not subcategoria_nombre:
                            subcategoria_nombre = categoria_nombre
                    else:
                        categoria_nombre = cat_sub_str
                        subcategoria_nombre = cat_sub_str


                    if categoria_nombre not in categorias_cache:
                        nombre_limpio = categoria_nombre.split('.')[0] if '.' in categoria_nombre else categoria_nombre
                        categoria_obj, _ = Categoria.objects.get_or_create(nombre=nombre_limpio[:100])
                        categorias_cache[categoria_nombre] = categoria_obj
                    
                    if subcategoria_nombre and subcategoria_nombre not in subcategorias_cache:
                        subcategoria_obj, _ = Subcategoria.objects.get_or_create(
                            nombre=subcategoria_nombre[:100], 
                            categoria=categorias_cache[categoria_nombre]
                        )
                        subcategorias_cache[subcategoria_nombre] = subcategoria_obj
                    else:
                        subcategoria_obj = subcategorias_cache.get(subcategoria_nombre)

                    # Marca
                    marca_nombre = fila.get('Marca', '').strip()
                    if marca_nombre and marca_nombre not in marcas_cache:
                        marca_obj, _ = Marca.objects.get_or_create(nombre=marca_nombre[:100])
                        marcas_cache[marca_nombre] = marca_obj
                    
                    # Proveedor
                    proveedor_nombre = fila.get('Proveedor', '').strip()
                    if proveedor_nombre and proveedor_nombre not in proveedores_cache:
                        proveedor_obj, _ = Proveedor.objects.get_or_create(nombre=proveedor_nombre[:100])
                        proveedores_cache[proveedor_nombre] = proveedor_obj
                    
                    # --- 2. Crear el objeto Producto (Temporal) ---
                    producto_obj = Producto(
                        nombre=nombre_producto[:255],
                        descripcion=fila.get('Descripscion', ''),
                        condicion=fila.get('Condicion', '').strip(),
                        estado="Vendido" if not fila.get('Stock') or fila.get('Stock', '0').strip() == '0' else "Disponible",
                        categoria=categorias_cache.get(categoria_nombre),
                        subcategoria=subcategorias_cache.get(subcategoria_nombre),
                        marca=marcas_cache.get(marca_nombre)
                    )
                    productos_a_crear.append(producto_obj)
                    
                    # --- 3. Crear el objeto VariacionProducto (Temporal) ---
                    sku_base = fila.get('ID', '').strip() or nombre_producto
                    
                    try:
                        precio_venta = decimal.Decimal(fila.get('Precio Venta', '0').replace(',', '.').strip())
                    except decimal.InvalidOperation:
                        precio_venta = decimal.Decimal('0.00')

                    try:
                        stock = int(fila.get('Stock', '0').strip())
                    except ValueError:
                        stock = 0

                    variacion_obj = VariacionProducto(
                        producto=producto_obj,
                        sku=sku_base[:50],
                        precio_venta=precio_venta,
                        stock=stock
                    )
                    variaciones_a_crear.append(variacion_obj)

                    # --- 4. Preparar datos de atributos para la Variacion ---
                    atributos_para_variacion = []
                    
                    # Atributo Talla
                    talla_val = fila.get('Talla', '').split('\n')[0].strip() # Usa solo la primera línea
                    if talla_val:
                        if 'Talla' not in atributos_cache:
                            atributo_talla, _ = Atributo.objects.get_or_create(nombre="Talla")
                            atributos_cache['Talla'] = atributo_talla
                        
                        valor_key = ('Talla', talla_val)
                        if valor_key not in valores_atributos_cache:
                            valor_talla, _ = ValorAtributo.objects.get_or_create(
                                atributo=atributos_cache['Talla'], valor=talla_val[:100]
                            )
                            valores_atributos_cache[valor_key] = valor_talla
                        
                        atributos_para_variacion.append(valores_atributos_cache[valor_key])
                    
                    # Atributo Color
                    colores_str = fila.get('Color', '').strip()
                    if colores_str:
                        if 'Color' not in atributos_cache:
                            atributo_color, _ = Atributo.objects.get_or_create(nombre="Color")
                            atributos_cache['Color'] = atributo_color

                        for color_val in colores_str.split(','):
                            color_val_strip = color_val.strip()
                            if color_val_strip:
                                valor_key = ('Color', color_val_strip)
                                if valor_key not in valores_atributos_cache:
                                    valor_color, _ = ValorAtributo.objects.get_or_create(
                                        atributo=atributos_cache['Color'], valor=color_val_strip[:100]
                                    )
                                    valores_atributos_cache[valor_key] = valor_color
                                    
                                atributos_para_variacion.append(valores_atributos_cache[valor_key])
                            
                    variaciones_con_atributos.append((variacion_obj, atributos_para_variacion))

                    # --- 5. Preparar datos de Medidas del Producto (Temporal) ---
                    medidas_data = parsear_medidas(fila.get('Talla', ''))
                    medidas_temp.append(
                        MedidasProducto(
                            variacion=variacion_obj, # Referencia a la VariacionProducto temporal
                            peso_gramos=medidas_data.get('peso', decimal.Decimal('0.00')),
                            alto_cm=medidas_data.get('alto', decimal.Decimal('0.00')),
                            ancho_cm=medidas_data.get('anchura', decimal.Decimal('0.00')),
                            profundidad_cm=medidas_data.get('longitud', decimal.Decimal('0.00'))
                        )
                    )
                    
                    # --- 6. Preparar datos de Compra y Venta (Temporal) ---
                    fecha_compra_str = fila.get('Fecha Compra', '').strip()
                    precio_compra_str = fila.get('Precio Compra', '0').replace(',', '.').strip()
                    
                    if fecha_compra_str and precio_compra_str:
                        try:
                            fecha_compra_dt = datetime.datetime.strptime(fecha_compra_str, '%Y-%m-%d').date()
                            precio_compra_dec = decimal.Decimal(precio_compra_str)
                            compra_obj = Compra(
                                producto=variacion_obj, # Referencia a la VariacionProducto temporal
                                cantidad=1,
                                precio_compra=precio_compra_dec,
                                proveedor=proveedores_cache.get(proveedor_nombre),
                                fecha_compra=fecha_compra_dt,
                                notas=fila.get('Notas', '')[:255]
                            )
                            compras_temp.append(compra_obj)
                        except (ValueError, decimal.InvalidOperation) as e:
                            print(f"❌ Advertencia: Error al parsear Compra en fila {i}: {e}")

                    fecha_venta_str = fila.get('Fecha Venta', '').strip()
                    precio_venta_str = fila.get('Precio Venta', '0').replace(',', '.').strip()
                    
                    if fecha_venta_str and precio_venta_str:
                        try:
                            fecha_venta_dt = datetime.datetime.strptime(fecha_venta_str, '%Y-%m-%d').date()
                            precio_total_dec = decimal.Decimal(precio_venta_str)
                            venta_obj = Venta(
                                producto=variacion_obj, # Referencia a la VariacionProducto temporal
                                cantidad=1,
                                precio_total=precio_total_dec,
                                fecha_venta=fecha_venta_dt,
                                notas=fila.get('Notas', '')[:255]
                            )
                            ventas_temp.append(venta_obj)
                        except (ValueError, decimal.InvalidOperation) as e:
                            print(f"❌ Advertencia: Error al parsear Venta en fila {i}: {e}")


                # --- FASE DE INSERCIÓN MASIVA (La Corrección Clave) ---
                
                # 1. Insertar Productos. Esto asigna el PK a las instancias en `productos_a_crear` que fueron guardadas.
                # Las instancias que fueron omitidas (por conflicto) NO tienen PK.
                Producto.objects.bulk_create(productos_a_crear, ignore_conflicts=True)

                # 2. Filtrar las variaciones: solo insertar aquellas cuyo producto padre *realmente* tiene un PK.
                variaciones_validas = [v for v in variaciones_a_crear if v.producto.pk]

                # 3. Insertar Variaciones. Esto asigna el PK a las instancias en `variaciones_validas` que fueron guardadas.
                VariacionProducto.objects.bulk_create(variaciones_validas, ignore_conflicts=True)
                
                # 4. Asignar el PK a los dependientes. Solo incluimos aquellos cuya Variación fue insertada (tiene PK).
                medidas_a_crear_final = [m for m in medidas_temp if m.variacion.pk]
                compras_a_crear_final = [c for c in compras_temp if c.producto.pk]
                ventas_a_crear_final = [v for v in ventas_temp if v.producto.pk]

                # 5. Insertar Medidas, Compra y Venta (ya con los PKs correctos)
                MedidasProducto.objects.bulk_create(medidas_a_crear_final, ignore_conflicts=True)
                Compra.objects.bulk_create(compras_a_crear_final, ignore_conflicts=True)
                Venta.objects.bulk_create(ventas_a_crear_final, ignore_conflicts=True)


                # 6. Manejar las relaciones Many-to-Many
                # Solo procesar las variaciones que fueron insertadas (tienen PK).
                for variacion_obj, atributos_list in variaciones_con_atributos:
                    if variacion_obj.pk:
                        # La variacion_obj es un objeto Python con su PK real.
                        # Podemos usarlo directamente para el set() de Many-to-Many.
                        variacion_obj.atributos.set(atributos_list)
                
            print(f"✅ ¡Importación masiva completada! Se procesaron {total_filas_procesadas} filas.")
            
        except FileNotFoundError:
            print(f"❌ Error: El archivo '{nombre_archivo}' no se encontró. Asegúrate de que esté en la misma carpeta que el script.")
        except Exception as e:
            # Deshace cualquier cambio en la base de datos si ocurre un error
            print(f"❌ Ocurrió un error inesperado: {e}")

if __name__ == '__main__':
    nombre_del_archivo_csv = 'Hoja de cálculo sin título.xlsx - Hoja 1.csv'  # Asegúrate de que el archivo CSV esté en la misma carpeta que este script
    importar_articulos_desde_csv(nombre_del_archivo_csv)