from flask import Flask, render_template, request, redirect, url_for, flash
import os
import sys

# Agregar el directorio raíz del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar el archivo database.py
import database as db

# Configuración de la plantilla
template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, 'Tipo_Vivienda', 'templates')

# Crear la aplicación Flask
app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'your_secret_key'  # Clave secreta para usar flash messages

# Ruta principal
@app.route('/')
def home():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM tipovivienda")
    myresult = cursor.fetchall()

    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()
    return render_template('Tipo_Vivienda.html', data=insertObject)

# Ruta para agregar un tipo de vivienda
@app.route('/tipovivienda', methods=['POST'])
def add_tipovivienda():
    codtipoviv = request.form['codtipoviv']
    nomtipoviv = request.form['nomtipoviv']
    
    if codtipoviv and nomtipoviv:
        cursor = db.database.cursor()

        # Verificar si el código ya existe
        cursor.execute("SELECT * FROM tipovivienda WHERE TipVivCod = %s", (codtipoviv,))
        existing_cod = cursor.fetchone()
        
        # Verificar si el nombre ya existe
        cursor.execute("SELECT * FROM tipovivienda WHERE TipVivNom = %s", (nomtipoviv,))
        existing_nom = cursor.fetchone()
        
        if existing_cod:
            flash('El código de tipo de vivienda ya existe. Por favor ingrese un código diferente.')
            cursor.close()
            return redirect(url_for('home'))
        elif existing_nom:
            flash('El nombre del tipo de vivienda ya existe. Por favor ingrese un nombre diferente.')
            cursor.close()
            return redirect(url_for('home'))

        sql = "INSERT INTO tipovivienda (TipVivCod, TipVivNom, TipVivEstReg) VALUES (%s, %s, 'A')"
        data = (codtipoviv, nomtipoviv)
        cursor.execute(sql, data)
        db.database.commit()
        cursor.close()
        flash('Tipo de vivienda insertado exitosamente.')
    return redirect(url_for('home'))

# Ruta para eliminar un tipo de vivienda
@app.route('/delete/<string:codtipoviv>')
def delete_tipovivienda(codtipoviv):
    cursor = db.database.cursor()
    sql = "DELETE FROM tipovivienda WHERE TipVivCod = %s"
    data = (codtipoviv,)
    cursor.execute(sql, data)
    db.database.commit()
    return redirect(url_for('home'))

# Ruta para editar un tipo de vivienda
@app.route('/edit/<string:codtipoviv>', methods=['POST'])
def edit_tipovivienda(codtipoviv):
    if 'action' in request.form:
        action = request.form['action']
        cursor = db.database.cursor()
        
        if action == 'inactivar':
            sql = "UPDATE tipovivienda SET TipVivEstReg='I' WHERE TipVivCod=%s"
            cursor.execute(sql, (codtipoviv,))
        elif action == 'activar':
            sql = "UPDATE tipovivienda SET TipVivEstReg='A' WHERE TipVivCod=%s"
            cursor.execute(sql, (codtipoviv,))
        elif action == 'edit':
            nomtipoviv = request.form['nomtipoviv']
            if nomtipoviv:
                # Verificar si el nombre ya existe para otros registros
                cursor.execute("SELECT * FROM tipovivienda WHERE TipVivNom = %s AND TipVivCod != %s", (nomtipoviv, codtipoviv))
                existing_nom = cursor.fetchone()
                if existing_nom:
                    flash('El nombre del tipo de vivienda ya existe. Por favor ingrese un nombre diferente.')
                    cursor.close()
                    return redirect(url_for('home'))

                sql = "UPDATE tipovivienda SET TipVivNom=%s WHERE TipVivCod=%s"
                cursor.execute(sql, (nomtipoviv, codtipoviv))
        
        db.database.commit()
        cursor.close()
        flash('Cambios guardados exitosamente.')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=4000)
