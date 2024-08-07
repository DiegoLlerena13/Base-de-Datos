from flask import Flask, render_template, request, redirect, url_for, flash,jsonify
import os
import sys
from mysql.connector import Error


# Agregar el directorio raíz del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Ahora puedes importar el archivo database.py
import database as db

template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, 'Zona_Urbana', 'templates')

app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'your_secret_key'  # Clave secreta para usar flash messages

@app.route('/')
def home():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM Zona_Urbana")
    myresult = cursor.fetchall()

    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columnNames, record)))
    
    cursor.execute("SELECT MunCod, MunNom FROM Municipio")
    municipios = cursor.fetchall()
    municipio_list = [{"MunCod": m[0], "MunNom": m[1]} for m in municipios]
    
    cursor.close()
    return render_template('Zona_Urbana.html', data=insertObject, municipios=municipio_list)

@app.route('/buscar_municipio', methods=['GET'])
def buscar_municipio():
    cursor = db.database.cursor()
    term = request.args.get('term', '')
    
    if not cursor:
        return jsonify({"error": "MySQL Connection not available"}), 500
    
    try:
        cursor.execute("SELECT MunCod, MunNom FROM Municipio WHERE MunNom LIKE %s OR MunCod LIKE %s", (f'%{term}%', f'%{term}%'))
        municipios = cursor.fetchall()
        municipio_list = [{"id": m[0], "text": f"{m[1]} ({m[0]})"} for m in municipios]
        return {'results': municipio_list}
    except Error as e:
        print(f"Error executing query: {e}")
        return jsonify({"error": "Error executing query"}), 500
    finally:
            cursor.close()


@app.route('/zona_urbana', methods=['POST'])
def add_zona():
    cod_zona = request.form['cod_zona']
    nom_zona = request.form['nom_zona']
    mun_cod = request.form['mun_cod']
    
    if cod_zona and nom_zona and mun_cod:
        cursor = db.database.cursor()

        # Verificar si el código ya existe
        cursor.execute("SELECT * FROM Zona_Urbana WHERE ZonCod = %s", (cod_zona,))
        existing_cod = cursor.fetchone()
        
        # Verificar si el nombre ya existe
        cursor.execute("SELECT * FROM Zona_Urbana WHERE ZonNom = %s", (nom_zona,))
        existing_nom = cursor.fetchone()
        
        if existing_cod:
            flash('El código de zona urbana ya existe. Por favor ingrese un código diferente.')
            cursor.close()
            return redirect(url_for('home'))
        elif existing_nom:
            flash('El nombre de la zona urbana ya existe. Por favor ingrese un nombre diferente.')
            cursor.close()
            return redirect(url_for('home'))

        sql = "INSERT INTO Zona_Urbana (ZonCod, ZonNom, ZonEstReg, MunCod) VALUES (%s, %s, 'A', %s)"
        data = (cod_zona, nom_zona, mun_cod)
        cursor.execute(sql, data)
        db.database.commit()
        cursor.close()
        flash('Zona urbana insertada exitosamente.')
    return redirect(url_for('home'))

@app.route('/edit/<string:cod_zona>', methods=['POST'])
def edit(cod_zona):
    if 'action' in request.form:
        action = request.form['action']
        cursor = db.database.cursor()

        if action == 'inactivar':
            sql = "UPDATE Zona_Urbana SET ZonEstReg='I' WHERE ZonCod=%s"
            cursor.execute(sql, (cod_zona,))
        elif action == 'activar':
            sql = "UPDATE Zona_Urbana SET ZonEstReg='A' WHERE ZonCod=%s"
            cursor.execute(sql, (cod_zona,))
        elif action == 'edit':
            nom_zona = request.form['nom_zona']
            mun_cod = request.form['mun_cod']
            if nom_zona and mun_cod:
                # Verificar si el nombre ya existe para otros registros
                cursor.execute("SELECT * FROM Zona_Urbana WHERE ZonNom = %s AND ZonCod != %s", (nom_zona, cod_zona))
                existing_nom = cursor.fetchone()
                if existing_nom:
                    flash('El nombre de la zona urbana ya existe. Por favor ingrese un nombre diferente.')
                    cursor.close()
                    return redirect(url_for('home'))

                sql = "UPDATE Zona_Urbana SET ZonNom=%s, MunCod=%s WHERE ZonCod=%s"
                cursor.execute(sql, (nom_zona, mun_cod, cod_zona))

        db.database.commit()
        cursor.close()
        flash('Cambios guardados exitosamente.')
    return redirect(url_for('home'))

@app.route('/delete/<string:cod_zona>')
def delete(cod_zona):
    cursor = db.database.cursor()
    sql = "DELETE FROM Zona_Urbana WHERE ZonCod = %s"
    data = (cod_zona,)
    cursor.execute(sql, data)
    db.database.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=4000)