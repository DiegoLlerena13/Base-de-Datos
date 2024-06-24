from flask import Flask, render_template, request, redirect, url_for, flash
import os
import sys

# Agregar el directorio raíz del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Ahora puedes importar el archivo database.py
import database as db

template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, 'ZonaUrbana', 'templates')

app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'your_secret_key'  # Clave secreta para usar flash messages

@app.route('/')
def home():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM zonaurbana")
    myresult = cursor.fetchall()

    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()
    return render_template('ZonaUrbana.html', data=insertObject)

@app.route('/zonaurbana', methods=['POST'])
def addzonaurbana():
    codzona = request.form['codzona']
    nomzona = request.form['nomzona']
    
    if codzona and nomzona:
        cursor = db.database.cursor()

        # Verificar si el código ya existe
        cursor.execute("SELECT * FROM zonaurbana WHERE ZUCod = %s", (codzona,))
        existing_cod = cursor.fetchone()
        
        # Verificar si el nombre ya existe
        cursor.execute("SELECT * FROM zonaurbana WHERE ZUNom = %s", (nomzona,))
        existing_nom = cursor.fetchone()
        
        if existing_cod:
            flash('El código de zona urbana ya existe. Por favor ingrese un código diferente.')
            cursor.close()
            return redirect(url_for('home'))
        elif existing_nom:
            flash('El nombre de la zona urbana ya existe. Por favor ingrese un nombre diferente.')
            cursor.close()
            return redirect(url_for('home'))

        sql = "INSERT INTO zonaurbana (ZUCod, ZUNom, ZUEstReg) VALUES (%s, %s, 'A')"
        data = (codzona, nomzona)
        cursor.execute(sql, data)
        db.database.commit()
        cursor.close()
        flash('Zona urbana insertada exitosamente.')
    return redirect(url_for('home'))

@app.route('/delete/<string:codzona>')
def delete(codzona):
    cursor = db.database.cursor()
    sql = "DELETE FROM zonaurbana WHERE ZUCod = %s"
    data = (codzona,)
    cursor.execute(sql, data)
    db.database.commit()
    return redirect(url_for('home'))

@app.route('/edit/<string:codzona>', methods=['POST'])
def edit(codzona):
    if 'action' in request.form:
        action = request.form['action']
        cursor = db.database.cursor()
        
        if action == 'inactivar':
            sql = "UPDATE zonaurbana SET ZUEstReg='I' WHERE ZUCod=%s"
            cursor.execute(sql, (codzona,))
        elif action == 'activar':
            sql = "UPDATE zonaurbana SET ZUEstReg='A' WHERE ZUCod=%s"
            cursor.execute(sql, (codzona,))
        elif action == 'edit':
            nomzona = request.form['nomzona']
            if nomzona:
                # Verificar si el nombre ya existe para otros registros
                cursor.execute("SELECT * FROM zonaurbana WHERE ZUNom = %s AND ZUCod != %s", (nomzona, codzona))
                existing_nom = cursor.fetchone()
                if existing_nom:
                    flash('El nombre de la zona urbana ya existe. Por favor ingrese un nombre diferente.')
                    cursor.close()
                    return redirect(url_for('home'))

                sql = "UPDATE zonaurbana SET ZUNom=%s WHERE ZUCod=%s"
                cursor.execute(sql, (nomzona, codzona))
        
        db.database.commit()
        cursor.close()
        flash('Cambios guardados exitosamente.')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=4000)
