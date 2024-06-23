from flask import Flask, render_template, request, redirect, url_for, flash
import os
import sys

# Agregar el directorio raíz del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Ahora puedes importar el archivo database.py
import database as db

template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, 'Persona', 'templates')

app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'your_secret_key'  # Clave secreta para usar flash messages

@app.route('/')
def home():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM Persona")
    myresult = cursor.fetchall()

    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()
    return render_template('Persona.html', data=insertObject)

@app.route('/persona', methods=['POST'])
def add_persona():
    per_cod = request.form['per_cod']
    per_nom = request.form['per_nom']
    per_ape_pat = request.form['per_ape_pat']
    per_ape_mat = request.form['per_ape_mat']
    fam_cod = request.form['fam_cod']
    tip_per_cod = request.form['tip_per_cod']
    
    if per_cod and per_nom and per_ape_pat and per_ape_mat and fam_cod and tip_per_cod:
        cursor = db.database.cursor()

        # Verificar si el código ya existe
        cursor.execute("SELECT * FROM Persona WHERE PerCod = %s", (per_cod,))
        existing_cod = cursor.fetchone()
        
        if existing_cod:
            flash('El código de persona ya existe. Por favor ingrese un código diferente.')
            cursor.close()
            return redirect(url_for('home'))

        sql = "INSERT INTO Persona (PerCod, PerNom, PerApePat, PerApeMat, FamCod, TipPerCod, PerEstReg) VALUES (%s, %s, %s, %s, %s, %s, 'A')"
        data = (per_cod, per_nom, per_ape_pat, per_ape_mat, fam_cod, tip_per_cod)
        cursor.execute(sql, data)
        db.database.commit()
        cursor.close()
        flash('Persona insertada exitosamente.')
    return redirect(url_for('home'))

@app.route('/delete/<int:per_cod>')
def delete(per_cod):
    cursor = db.database.cursor()
    sql = "DELETE FROM Persona WHERE PerCod = %s"
    data = (per_cod,)
    cursor.execute(sql, data)
    db.database.commit()
    cursor.close()
    return redirect(url_for('home'))

@app.route('/edit/<int:per_cod>', methods=['POST'])
def edit(per_cod):
    if 'action' in request.form:
        action = request.form['action']
        cursor = db.database.cursor()
        
        if action == 'inactivar':
            sql = "UPDATE Persona SET PerEstReg='I' WHERE PerCod=%s"
            cursor.execute(sql, (per_cod,))
        elif action == 'activar':
            sql = "UPDATE Persona SET PerEstReg='A' WHERE PerCod=%s"
            cursor.execute(sql, (per_cod,))
        elif action == 'edit':
            per_nom = request.form['per_nom']
            per_ape_pat = request.form['per_ape_pat']
            per_ape_mat = request.form['per_ape_mat']
            fam_cod = request.form['fam_cod']
            tip_per_cod = request.form['tip_per_cod']
            
            if per_nom and per_ape_pat and per_ape_mat and fam_cod and tip_per_cod:
                sql = """UPDATE Persona SET PerNom=%s, PerApePat=%s, PerApeMat=%s, FamCod=%s, TipPerCod=%s 
                         WHERE PerCod=%s"""
                cursor.execute(sql, (per_nom, per_ape_pat, per_ape_mat, fam_cod, tip_per_cod, per_cod))
        
        db.database.commit()
        cursor.close()
        flash('Cambios guardados exitosamente.')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=4000)
