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
    cursor.execute("SELECT * FROM municipio")
    myresult = cursor.fetchall()

    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()
    return render_template('Municipio.html', data=insertObject)

@app.route('/municipio', methods=['POST'])
def add_municipio():
    codmun = request.form['codmun']
    nommun = request.form['nommun']
    
    if codmun and nommun:
        cursor = db.database.cursor()

        # Verificar si el código ya existe
        cursor.execute("SELECT * FROM municipio WHERE MunCod = %s", (codmun,))
        existing_cod = cursor.fetchone()
        
        # Verificar si el nombre ya existe
        cursor.execute("SELECT * FROM municipio WHERE MunNom = %s", (nommun,))
        existing_nom = cursor.fetchone()
        
        if existing_cod:
            flash('El código de municipio ya existe. Por favor ingrese un código diferente.')
            cursor.close()
            return redirect(url_for('home'))
        elif existing_nom:
            flash('El nombre del municipio ya existe. Por favor ingrese un nombre diferente.')
            cursor.close()
            return redirect(url_for('home'))

        sql = "INSERT INTO municipio (MunCod, MunNom, MunEstReg) VALUES (%s, %s, 'A')"
        data = (codmun, nommun)
        cursor.execute(sql, data)
        db.database.commit()
        cursor.close()
        flash('Municipio insertado exitosamente.')
    return redirect(url_for('home'))

@app.route('/delete/<string:codmun>')
def delete_municipio(codmun):
    cursor = db.database.cursor()
    sql = "DELETE FROM municipio WHERE MunCod = %s"
    data = (codmun,)
    cursor.execute(sql, data)
    db.database.commit()
    return redirect(url_for('home'))

@app.route('/edit/<string:codmun>', methods=['POST'])
def edit_municipio(codmun):
    if 'action' in request.form:
        action = request.form['action']
        cursor = db.database.cursor()
        
        if action == 'inactivar':
            sql = "UPDATE municipio SET MunEstReg='I' WHERE MunCod=%s"
            cursor.execute(sql, (codmun,))
        elif action == 'activar':
            sql = "UPDATE municipio SET MunEstReg='A' WHERE MunCod=%s"
            cursor.execute(sql, (codmun,))
        elif action == 'edit':
            nommun = request.form['nommun']
            if nommun:
                # Verificar si el nombre ya existe para otros registros
                cursor.execute("SELECT * FROM municipio WHERE MunNom = %s AND MunCod != %s", (nommun, codmun))
                existing_nom = cursor.fetchone()
                if existing_nom:
                    flash('El nombre del municipio ya existe. Por favor ingrese un nombre diferente.')
                    cursor.close()
                    return redirect(url_for('home'))

                sql = "UPDATE municipio SET MunNom=%s WHERE MunCod=%s"
                cursor.execute(sql, (nommun, codmun))
        
        db.database.commit()
        cursor.close()
        flash('Cambios guardados exitosamente.')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=4000)
