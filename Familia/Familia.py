from flask import Flask, render_template, request, redirect, url_for, flash
import os
import sys

# Agregar el directorio raíz del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Ahora puedes importar el archivo database.py
import database as db

template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, 'Familia', 'templates')

app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'your_secret_key'  # Clave secreta para usar flash messages

@app.route('/')
def home():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM Familia")
    myresult = cursor.fetchall()

    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()
    return render_template('Familia.html', data=insertObject)

@app.route('/familia', methods=['POST'])
def addfamilia():
    famcod = request.form['famcod']
    famnom = request.form['famnom']
    famnumint = request.form['famnumint']
    
    if famcod and famnom and famnumint:
        cursor = db.database.cursor()

        # Verificar si el código ya existe
        cursor.execute("SELECT * FROM Familia WHERE FamCod = %s", (famcod,))
        existing_cod = cursor.fetchone()
        
        # Verificar si el nombre ya existe
        cursor.execute("SELECT * FROM Familia WHERE FamNom = %s", (famnom,))
        existing_nom = cursor.fetchone()
        
        if existing_cod:
            flash('El código de familia ya existe. Por favor ingrese un código diferente.')
            cursor.close()
            return redirect(url_for('home'))
        elif existing_nom:
            flash('El nombre de la familia ya existe. Por favor ingrese un nombre diferente.')
            cursor.close()
            return redirect(url_for('home'))

        sql = "INSERT INTO Familia (FamCod, FamNom, FamNumInt, FamEstReg) VALUES (%s, %s, %s, 'A')"
        data = (famcod, famnom, famnumint)
        cursor.execute(sql, data)
        db.database.commit()
        cursor.close()
        flash('Familia insertada exitosamente.')
    return redirect(url_for('home'))

@app.route('/delete/<string:famcod>')
def delete(famcod):
    cursor = db.database.cursor()
    sql = "DELETE FROM Familia WHERE FamCod = %s"
    data = (famcod,)
    cursor.execute(sql, data)
    db.database.commit()
    return redirect(url_for('home'))

@app.route('/edit/<string:famcod>', methods=['POST'])
def edit(famcod):
    if 'action' in request.form:
        action = request.form['action']
        cursor = db.database.cursor()
        
        if action == 'inactivar':
            sql = "UPDATE Familia SET FamEstReg='I' WHERE FamCod=%s"
            cursor.execute(sql, (famcod,))
        elif action == 'activar':
            sql = "UPDATE Familia SET FamEstReg='A' WHERE FamCod=%s"
            cursor.execute(sql, (famcod,))
        elif action == 'edit':
            famnom = request.form['famnom']
            famnumint = request.form['famnumint']
            if famnom and famnumint:
                # Verificar si el nombre ya existe para otros registros
                cursor.execute("SELECT * FROM Familia WHERE FamNom = %s AND FamCod != %s", (famnom, famcod))
                existing_nom = cursor.fetchone()
                if existing_nom:
                    flash('El nombre de la familia ya existe. Por favor ingrese un nombre diferente.')
                    cursor.close()
                    return redirect(url_for('home'))

                sql = "UPDATE Familia SET FamNom=%s, FamNumInt=%s WHERE FamCod=%s"
                cursor.execute(sql, (famnom, famnumint, famcod))
        
        db.database.commit()
        cursor.close()
        flash('Cambios guardados exitosamente.')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=4000)
