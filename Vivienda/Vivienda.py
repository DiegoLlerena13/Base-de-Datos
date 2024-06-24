from flask import Flask, render_template, request, redirect, url_for, flash
import os
import sys

# Agregar el directorio raíz del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Ahora puedes importar el archivo database.py
import database as db

template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, 'Vivienda', 'templates')

app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'your_secret_key'  # Clave secreta para usar flash messages

@app.route('/')
def home():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM vivienda")
    myresult = cursor.fetchall()

    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()
    return render_template('Vivienda.html', data=insertObject)

@app.route('/vivienda', methods=['POST'])
def addvivienda():
    codviv = request.form['codviv']
    nomviv = request.form['nomviv']
    
    if codviv and nomviv:
        cursor = db.database.cursor()

        # Verificar si el código ya existe
        cursor.execute("SELECT * FROM vivienda WHERE VivCod = %s", (codviv,))
        existing_cod = cursor.fetchone()
        
        # Verificar si el nombre ya existe
        cursor.execute("SELECT * FROM vivienda WHERE VivNom = %s", (nomviv,))
        existing_nom = cursor.fetchone()
        
        if existing_cod:
            flash('El código de vivienda ya existe. Por favor ingrese un código diferente.')
            cursor.close()
            return redirect(url_for('home'))
        elif existing_nom:
            flash('El nombre de la vivienda ya existe. Por favor ingrese un nombre diferente.')
            cursor.close()
            return redirect(url_for('home'))

        sql = "INSERT INTO vivienda (VivCod, VivNom, VivEstReg) VALUES (%s, %s, 'A')"
        data = (codviv, nomviv)
        cursor.execute(sql, data)
        db.database.commit()
        cursor.close()
        flash('Vivienda insertada exitosamente.')
    return redirect(url_for('home'))

@app.route('/delete/<string:codviv>')
def delete(codviv):
    cursor = db.database.cursor()
    sql = "DELETE FROM vivienda WHERE VivCod = %s"
    data = (codviv,)
    cursor.execute(sql, data)
    db.database.commit()
    return redirect(url_for('home'))

@app.route('/edit/<string:codviv>', methods=['POST'])
def edit(codviv):
    if 'action' in request.form:
        action = request.form['action']
        cursor = db.database.cursor()
        
        if action == 'inactivar':
            sql = "UPDATE vivienda SET VivEstReg='I' WHERE VivCod=%s"
            cursor.execute(sql, (codviv,))
        elif action == 'activar':
            sql = "UPDATE vivienda SET VivEstReg='A' WHERE VivCod=%s"
            cursor.execute(sql, (codviv,))
        elif action == 'edit':
            nomviv = request.form['nomviv']
            if nomviv:
                # Verificar si el nombre ya existe para otros registros
                cursor.execute("SELECT * FROM vivienda WHERE VivNom = %s AND VivCod != %s", (nomviv, codviv))
                existing_nom = cursor.fetchone()
                if existing_nom:
                    flash('El nombre de la vivienda ya existe. Por favor ingrese un nombre diferente.')
                    cursor.close()
                    return redirect(url_for('home'))

                sql = "UPDATE vivienda SET VivNom=%s WHERE VivCod=%s"
                cursor.execute(sql, (nomviv, codviv))
        
        db.database.commit()
        cursor.close()
        flash('Cambios guardados exitosamente.')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=4000)
