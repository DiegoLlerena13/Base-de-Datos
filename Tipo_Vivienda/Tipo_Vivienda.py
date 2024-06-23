from flask import Flask, render_template, request, redirect, url_for, flash
import os
import sys

# Agregar el directorio raíz del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Ahora puedes importar el archivo database.py
import database as db

template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, 'Tipo_Vivienda', 'templates')

app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'your_secret_key'  # Clave secreta para usar flash messages

@app.route('/')
def home():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM region")
    myresult = cursor.fetchall()

    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()
    return render_template('Tipo_Vivienda.html', data=insertObject)

@app.route('/region', methods=['POST'])
def addregion():
    codreg = request.form['codreg']
    nomreg = request.form['nomreg']
    
    if codreg and nomreg:
        cursor = db.database.cursor()

        # Verificar si el código ya existe
        cursor.execute("SELECT * FROM region WHERE RegCod = %s", (codreg,))
        existing_cod = cursor.fetchone()
        
        # Verificar si el nombre ya existe
        cursor.execute("SELECT * FROM region WHERE RegNom = %s", (nomreg,))
        existing_nom = cursor.fetchone()
        
        if existing_cod:
            flash('El código de región ya existe. Por favor ingrese un código diferente.')
            cursor.close()
            return redirect(url_for('home'))
        elif existing_nom:
            flash('El nombre de la región ya existe. Por favor ingrese un nombre diferente.')
            cursor.close()
            return redirect(url_for('home'))

        sql = "INSERT INTO region (RegCod, RegNom, RegEstReg) VALUES (%s, %s, 'A')"
        data = (codreg, nomreg)
        cursor.execute(sql, data)
        db.database.commit()
        cursor.close()
        flash('Región insertada exitosamente.')
    return redirect(url_for('home'))

@app.route('/delete/<string:codreg>')
def delete(codreg):
    cursor = db.database.cursor()
    sql = "DELETE FROM region WHERE RegCod = %s"
    data = (codreg,)
    cursor.execute(sql, data)
    db.database.commit()
    return redirect(url_for('home'))

@app.route('/edit/<string:codreg>', methods=['POST'])
def edit(codreg):
    if 'action' in request.form:
        action = request.form['action']
        cursor = db.database.cursor()
        
        if action == 'inactivar':
            sql = "UPDATE region SET RegEstReg='I' WHERE RegCod=%s"
            cursor.execute(sql, (codreg,))
        elif action == 'activar':
            sql = "UPDATE region SET RegEstReg='A' WHERE RegCod=%s"
            cursor.execute(sql, (codreg,))
        elif action == 'edit':
            nomreg = request.form['nomreg']
            if nomreg:
                # Verificar si el nombre ya existe para otros registros
                cursor.execute("SELECT * FROM region WHERE RegNom = %s AND RegCod != %s", (nomreg, codreg))
                existing_nom = cursor.fetchone()
                if existing_nom:
                    flash('El nombre de la región ya existe. Por favor ingrese un nombre diferente.')
                    cursor.close()
                    return redirect(url_for('home'))

                sql = "UPDATE region SET RegNom=%s WHERE RegCod=%s"
                cursor.execute(sql, (nomreg, codreg))
        
        db.database.commit()
        cursor.close()
        flash('Cambios guardados exitosamente.')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=4000)
