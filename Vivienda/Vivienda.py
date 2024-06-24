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
    cursor.execute("SELECT * FROM Vivienda")
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
    vivcal = request.form['vivcal']
    vivnum = request.form['vivnum']
    vivcodpos = request.form['vivcodpos']
    vivmet = request.form['vivmet']
    vivocu = request.form['vivocu']
    zoncod = request.form['zoncod']
    tipvivcod = request.form['tipvivcod']

    if codviv and vivcal and vivnum and vivcodpos and vivmet and vivocu and zoncod and tipvivcod:
        cursor = db.database.cursor()

        # Verificar si el código ya existe
        cursor.execute("SELECT * FROM Vivienda WHERE VivCod = %s", (codviv,))
        existing_cod = cursor.fetchone()

        if existing_cod:
            flash('El código de Vivienda ya existe. Por favor ingrese un código diferente.')
            cursor.close()
            return redirect(url_for('home'))

        sql = """
        INSERT INTO Vivienda (VivCod, VivCal, VivNum, VivCodPos, VivMet, VivOcu, ZonCod, TipVivCod, VivEstReg) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s,'A')
        """
        data = (codviv, vivcal, vivnum, vivcodpos, vivmet, vivocu, zoncod, tipvivcod)
        cursor.execute(sql, data)
        db.database.commit()
        cursor.close()
        flash('Vivienda insertada exitosamente.')
    return redirect(url_for('home'))

@app.route('/delete/<string:codviv>')
def delete(codviv):
    cursor = db.database.cursor()
    sql = "DELETE FROM Vivienda WHERE VivCod = %s"
    data = (codviv,)
    cursor.execute(sql, data)
    db.database.commit()
    flash('Vivienda eliminada exitosamente.')
    return redirect(url_for('home'))

@app.route('/edit/<string:codviv>', methods=['POST'])
def edit(codviv):
    if 'action' in request.form:
        action = request.form['action']
        cursor = db.database.cursor()

        if action == 'inactivar':
            sql = "UPDATE Vivienda SET VivEstReg='I' WHERE VivCod=%s"
            cursor.execute(sql, (codviv,))
        elif action == 'activar':
            sql = "UPDATE Vivienda SET VivEstReg='A' WHERE VivCod=%s"
            cursor.execute(sql, (codviv,))
        elif action == 'edit':
            vivcal = request.form['vivcal']
            vivnum = request.form['vivnum']
            vivcodpos = request.form['vivcodpos']
            vivmet = request.form['vivmet']
            vivocu = request.form['vivocu']
            zoncod = request.form['zoncod']
            tipvivcod = request.form['tipvivcod']

            if vivcal and vivnum and vivcodpos and vivmet and vivocu and zoncod and tipvivcod:
                sql = """
                UPDATE Vivienda 
                SET VivCal=%s, VivNum=%s, VivCodPos=%s, VivMet=%s, VivOcu=%s, ZonCod=%s, TipVivCod=%s 
                WHERE VivCod=%s
                """
                cursor.execute(sql, (vivcal, vivnum, vivcodpos, vivmet, vivocu, zoncod, tipvivcod, codviv))

        db.database.commit()
        cursor.close()
        flash('Cambios guardados exitosamente.')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=4000)
