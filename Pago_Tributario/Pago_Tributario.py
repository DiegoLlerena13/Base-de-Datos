from flask import Flask, render_template, request, redirect, url_for, flash
import os
import sys

# Agregar el directorio raíz del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Ahora puedes importar el archivo database.py
import database as db

template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, 'Pago_Tributario', 'templates')

app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'your_secret_key'  # Clave secreta para usar flash messages

@app.route('/')
def home():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM Pago_Tributario")
    myresult = cursor.fetchall()

    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()
    return render_template('Pago_Tributario.html', data=insertObject)

@app.route('/pago_tributario', methods=['POST'])
def add_pago_tributario():
    pagtricod = request.form['pagtricod']
    pagtrifec = request.form['pagtrifec']
    cascoc = request.form['cascod']
    
    if pagtricod and cascoc:
        cursor = db.database.cursor()

        # Verificar si el código ya existe
        cursor.execute("SELECT * FROM Pago_Tributario WHERE PagTriCod = %s", (pagtricod,))
        existing_cod = cursor.fetchone()
        
        if existing_cod:
            flash('El código de pago tributario ya existe. Por favor ingrese un código diferente.')
            cursor.close()
            return redirect(url_for('home'))

        sql = "INSERT INTO Pago_Tributario (PagTriCod, PagTriFec, CasCod, PagTriEstReg) VALUES (%s, %s, %s, 'A')"
        data = (pagtricod, pagtrifec, cascoc)
        cursor.execute(sql, data)
        db.database.commit()
        cursor.close()
        flash('Pago tributario insertado exitosamente.')
    return redirect(url_for('home'))

@app.route('/delete/<string:pagtricod>')
def delete(pagtricod):
    cursor = db.database.cursor()
    sql = "DELETE FROM Pago_Tributario WHERE PagTriCod = %s"
    data = (pagtricod,)
    cursor.execute(sql, data)
    db.database.commit()
    return redirect(url_for('home'))

@app.route('/edit/<string:pagtricod>', methods=['POST'])
def edit(pagtricod):
    if 'action' in request.form:
        action = request.form['action']
        cursor = db.database.cursor()
        
        if action == 'inactivar':
            sql = "UPDATE Pago_Tributario SET PagTriEstReg='I' WHERE PagTriCod=%s"
            cursor.execute(sql, (pagtricod,))
        elif action == 'activar':
            sql = "UPDATE Pago_Tributario SET PagTriEstReg='A' WHERE PagTriCod=%s"
            cursor.execute(sql, (pagtricod,))
        elif action == 'edit':
            pagtrifec = request.form['pagtrifec']
            cascoc = request.form['cascod']
            if pagtrifec and cascoc:
                sql = "UPDATE Pago_Tributario SET PagTriFec=%s, CasCod=%s WHERE PagTriCod=%s"
                cursor.execute(sql, (pagtrifec, cascoc, pagtricod))
        
        db.database.commit()
        cursor.close()
        flash('Cambios guardados exitosamente.')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=4000)

