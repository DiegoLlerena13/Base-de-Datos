from flask import Flask, render_template, request, redirect, url_for, flash
import os
import sys

# Agregar el directorio raíz del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Ahora puedes importar el archivo database.py
import database as db

template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, 'Municipio', 'templates')

app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'your_secret_key'  # Clave secreta para usar flash messages

@app.route('/')
def home():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM Municipio")
    myresult = cursor.fetchall()

    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columnNames, record)))
    
    # Obtener los códigos de región
    cursor.execute("SELECT RegCod, RegNom FROM Region")
    regiones = cursor.fetchall()
    cursor.close()
    return render_template('Municipio.html', data=insertObject, regiones=regiones)

@app.route('/municipio', methods=['POST'])
def add_municipio():
    codmun = request.form['codmun']
    nommun = request.form['nommun']
    preanu = request.form['preanu']
    numviv = request.form['numviv']
    regcod = request.form['regcod']
    
    if codmun and nommun and preanu and numviv and regcod:
        cursor = db.database.cursor()

        # Verificar si el código ya existe
        cursor.execute("SELECT * FROM Municipio WHERE MunCod = %s", (codmun,))
        existing_cod = cursor.fetchone()
        
        # Verificar si el nombre ya existe
        cursor.execute("SELECT * FROM Municipio WHERE MunNom = %s", (nommun,))
        existing_nom = cursor.fetchone()
        
        if existing_cod:
            flash('El código de Municipio ya existe. Por favor ingrese un código diferente.')
            cursor.close()
            return redirect(url_for('home'))
        elif existing_nom:
            flash('El nombre del Municipio ya existe. Por favor ingrese un nombre diferente.')
            cursor.close()
            return redirect(url_for('home'))

        sql = "INSERT INTO Municipio (MunCod, MunNom, MunPreAnu, MunNumViv, MunEstReg, RegCod) VALUES (%s, %s, %s, %s, 'A', %s)"
        data = (codmun, nommun, preanu, numviv, regcod)
        cursor.execute(sql, data)
        db.database.commit()
        cursor.close()
        flash('Municipio insertado exitosamente.')
    return redirect(url_for('home'))

@app.route('/delete/<string:codmun>')
def delete_municipio(codmun):
    cursor = db.database.cursor()
    sql = "DELETE FROM Municipio WHERE MunCod = %s"
    data = (codmun,)
    cursor.execute(sql, data)
    db.database.commit()
    cursor.close()
    flash('Municipio eliminado exitosamente.')
    return redirect(url_for('home'))

@app.route('/edit/<string:codmun>', methods=['POST'])
def edit_municipio(codmun):
    if 'action' in request.form:
        action = request.form['action']
        cursor = db.database.cursor()
        
        if action == 'inactivar':
            sql = "UPDATE Municipio SET MunEstReg='I' WHERE MunCod=%s"
            cursor.execute(sql, (codmun,))
        elif action == 'activar':
            sql = "UPDATE Municipio SET MunEstReg='A' WHERE MunCod=%s"
            cursor.execute(sql, (codmun,))
        elif action == 'edit':
            nommun = request.form['nommun']
            preanu = request.form['preanu']
            numviv = request.form['numviv']
            regcod = request.form['regcod']
            
            if nommun and preanu and numviv and regcod:
                # Verificar si el nombre ya existe para otros registros
                cursor.execute("SELECT * FROM Municipio WHERE MunNom = %s AND MunCod != %s", (nommun, codmun))
                existing_nom = cursor.fetchone()
                if existing_nom:
                    flash('El nombre del municipio ya existe. Por favor ingrese un nombre diferente.')
                    cursor.close()
                    return redirect(url_for('home'))

                sql = "UPDATE Municipio SET MunNom=%s, MunPreAnu=%s, MunNumViv=%s, RegCod=%s WHERE MunCod=%s"
                cursor.execute(sql, (nommun, preanu, numviv, regcod, codmun))
        
        db.database.commit()
        cursor.close()
        flash('Cambios guardados exitosamente.')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=4000)
