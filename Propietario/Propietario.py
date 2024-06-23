from flask import Flask, render_template, request, redirect, url_for, flash
import os
import sys

# Agregar el directorio raíz del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Ahora puedes importar el archivo database.py
import database as db

template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, 'Propietario', 'templates')

app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'your_secret_key'  # Clave secreta para usar flash messages

@app.route('/')
def home():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM Propietario")
    myresult = cursor.fetchall()

    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()
    return render_template('Propietario.html', data=insertObject)

@app.route('/propietario', methods=['POST'])
def add_propietario():
    pro_cod = request.form['pro_cod']
    pro_pag_tri = request.form['pro_pag_tri']
    pro_mon_ing_fam = request.form['pro_mon_ing_fam']
    per_cod = request.form['per_cod']
    fam_cod = request.form['fam_cod']
    
    if pro_cod and pro_pag_tri and pro_mon_ing_fam and per_cod and fam_cod:
        cursor = db.database.cursor()

        # Verificar si el código ya existe
        cursor.execute("SELECT * FROM Propietario WHERE ProCod = %s", (pro_cod,))
        existing_cod = cursor.fetchone()
        
        if existing_cod:
            flash('El código de propietario ya existe. Por favor ingrese un código diferente.')
            cursor.close()
            return redirect(url_for('home'))

        sql = "INSERT INTO Propietario (ProCod, ProPagTri, ProMonIngFam, PerCod, FamCod, ProEstReg) VALUES (%s, %s, %s, %s, %s, 'A')"
        data = (pro_cod, pro_pag_tri, pro_mon_ing_fam, per_cod, fam_cod)
        cursor.execute(sql, data)
        db.database.commit()
        cursor.close()
        flash('Propietario insertado exitosamente.')
    return redirect(url_for('home'))

@app.route('/delete/<int:pro_cod>')
def delete(pro_cod):
    cursor = db.database.cursor()
    sql = "DELETE FROM Propietario WHERE ProCod = %s"
    data = (pro_cod,)
    cursor.execute(sql, data)
    db.database.commit()
    cursor.close()
    return redirect(url_for('home'))

@app.route('/edit/<int:pro_cod>', methods=['POST'])
def edit(pro_cod):
    if 'action' in request.form:
        action = request.form['action']
        cursor = db.database.cursor()
        
        if action == 'inactivar':
            sql = "UPDATE Propietario SET ProEstReg='I' WHERE ProCod=%s"
            cursor.execute(sql, (pro_cod,))
        elif action == 'activar':
            sql = "UPDATE Propietario SET ProEstReg='A' WHERE ProCod=%s"
            cursor.execute(sql, (pro_cod,))
        elif action == 'edit':
            pro_pag_tri = request.form['pro_pag_tri']
            pro_mon_ing_fam = request.form['pro_mon_ing_fam']
            per_cod = request.form['per_cod']
            fam_cod = request.form['fam_cod']
            
            if pro_pag_tri and pro_mon_ing_fam and per_cod and fam_cod:
                sql = """UPDATE Propietario SET ProPagTri=%s, ProMonIngFam=%s, PerCod=%s, FamCod=%s 
                         WHERE ProCod=%s"""
                cursor.execute(sql, (pro_pag_tri, pro_mon_ing_fam, per_cod, fam_cod, pro_cod))
        
        db.database.commit()
        cursor.close()
        flash('Cambios guardados exitosamente.')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=4000)
