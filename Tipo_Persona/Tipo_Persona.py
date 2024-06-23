from flask import Flask, render_template, request, redirect, url_for, flash
import os
import sys

# Agregar el directorio raíz del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Ahora puedes importar el archivo database.py
import database as db

template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, 'Tipo_Persona', 'templates')

app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'your_secret_key'  # Clave secreta para usar flash messages

@app.route('/')
def home():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM Tipo_Persona")
    myresult = cursor.fetchall()

    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()
    return render_template('Tipo_Persona.html', data=insertObject)

@app.route('/tipopersona', methods=['POST'])
def add_tipopersona():
    tip_per_cod = request.form['tip_per_cod']
    tip_per_des = request.form['tip_per_des']
    
    if tip_per_cod and tip_per_des:
        cursor = db.database.cursor()

        # Verificar si el código ya existe
        cursor.execute("SELECT * FROM Tipo_Persona WHERE TipPerCod = %s", (tip_per_cod,))
        existing_cod = cursor.fetchone()
        
        # Verificar si el nombre ya existe
        cursor.execute("SELECT * FROM Tipo_Persona WHERE TipPerDes = %s", (tip_per_des,))
        existing_des = cursor.fetchone()
        
        if existing_cod:
            flash('El código de tipo persona ya existe. Por favor ingrese un código diferente.')
            cursor.close()
            return redirect(url_for('home'))
        elif existing_des:
            flash('La descripción de tipo persona ya existe. Por favor ingrese una descripción diferente.')
            cursor.close()
            return redirect(url_for('home'))

        sql = "INSERT INTO Tipo_Persona (TipPerCod, TipPerDes, TipVivEstReg) VALUES (%s, %s, 'A')"
        data = (tip_per_cod, tip_per_des)
        cursor.execute(sql, data)
        db.database.commit()
        cursor.close()
        flash('Tipo de Persona insertado exitosamente.')
    return redirect(url_for('home'))

@app.route('/delete/<int:tip_per_cod>')
def delete(tip_per_cod):
    cursor = db.database.cursor()
    sql = "DELETE FROM Tipo_Persona WHERE TipPerCod = %s"
    data = (tip_per_cod,)
    cursor.execute(sql, data)
    db.database.commit()
    cursor.close()
    return redirect(url_for('home'))

@app.route('/edit/<int:tip_per_cod>', methods=['POST'])
def edit(tip_per_cod):
    if 'action' in request.form:
        action = request.form['action']
        cursor = db.database.cursor()
        
        if action == 'inactivar':
            sql = "UPDATE Tipo_Persona SET TipVivEstReg='I' WHERE TipPerCod=%s"
            cursor.execute(sql, (tip_per_cod,))
        elif action == 'activar':
            sql = "UPDATE Tipo_Persona SET TipVivEstReg='A' WHERE TipPerCod=%s"
            cursor.execute(sql, (tip_per_cod,))
        elif action == 'edit':
            tip_per_des = request.form['tip_per_des']
            if tip_per_des:
                # Verificar si la descripción ya existe para otros registros
                cursor.execute("SELECT * FROM Tipo_Persona WHERE TipPerDes = %s AND TipPerCod != %s", (tip_per_des, tip_per_cod))
                existing_des = cursor.fetchone()
                if existing_des:
                    flash('La descripción de tipo persona ya existe. Por favor ingrese una descripción diferente.')
                    cursor.close()
                    return redirect(url_for('home'))

                sql = "UPDATE Tipo_Persona SET TipPerDes=%s WHERE TipPerCod=%s"
                cursor.execute(sql, (tip_per_des, tip_per_cod))
        
        db.database.commit()
        cursor.close()
        flash('Cambios guardados exitosamente.')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=4000)
