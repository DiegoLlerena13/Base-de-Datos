from flask import Flask, render_template, request, redirect, url_for, flash
import os
import sys

# Agregar el directorio raíz del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Ahora puedes importar el archivo database.py
import database as db

template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, 'Casa', 'templates')

app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'your_secret_key'  # Clave secreta para usar flash messages

@app.route('/')
def home():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM Casa")
    myresult = cursor.fetchall()

    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()
    return render_template('Casa.html', data=insertObject)

@app.route('/casa', methods=['POST'])
def add_casa():
    cascod = request.form['cascod']
    casesc = request.form['casesc']
    cascod_blo = request.form['cascod_blo']
    caspla = request.form['caspla']
    casnum_pue = request.form['casnum_pue']
    casmet = request.form['casmet']
    vivcod = request.form['vivcod']
    famcod = request.form['famcod']
    
    if cascod and vivcod and famcod:
        cursor = db.database.cursor()

        # Verificar si el código ya existe
        cursor.execute("SELECT * FROM Casa WHERE CasCod = %s", (cascod,))
        existing_cascod = cursor.fetchone()
        
        if existing_cascod:
            flash('El código de casa ya existe. Por favor ingrese un código diferente.')
            cursor.close()
            return redirect(url_for('home'))

        sql = """
        INSERT INTO Casa (CasCod, CasEsc, CasCodBlo, CasPla, CasNumPue, CasMet, VivCod, FamCod, CasEstReg) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'A')
        """
        data = (cascod, casesc, cascod_blo, caspla, casnum_pue, casmet, vivcod, famcod)
        cursor.execute(sql, data)
        db.database.commit()
        cursor.close()
        flash('Casa insertada exitosamente.')
    return redirect(url_for('home'))

@app.route('/delete/<int:cascod>')
def delete(cascod):
    cursor = db.database.cursor()
    sql = "DELETE FROM Casa WHERE CasCod = %s"
    data = (cascod,)
    cursor.execute(sql, data)
    db.database.commit()
    return redirect(url_for('home'))

@app.route('/edit/<int:cascod>', methods=['POST'])
def edit(cascod):
    if 'action' in request.form:
        action = request.form['action']
        cursor = db.database.cursor()
        
        if action == 'inactivar':
            sql = "UPDATE Casa SET CasEstReg='I' WHERE CasCod=%s"
            cursor.execute(sql, (cascod,))
        elif action == 'activar':
            sql = "UPDATE Casa SET CasEstReg='A' WHERE CasCod=%s"
            cursor.execute(sql, (cascod,))
        elif action == 'edit':
            casesc = request.form['casesc']
            cascod_blo = request.form['cascod_blo']
            caspla = request.form['caspla']
            casnum_pue = request.form['casnum_pue']
            casmet = request.form['casmet']
            vivcod = request.form['vivcod']
            famcod = request.form['famcod']

            sql = """
            UPDATE Casa 
            SET CasEsc=%s, CasCodBlo=%s, CasPla=%s, CasNumPue=%s, CasMet=%s, VivCod=%s, FamCod=%s 
            WHERE CasCod=%s
            """
            data = (casesc, cascod_blo, caspla, casnum_pue, casmet, vivcod, famcod, cascod)
            cursor.execute(sql, data)
        
        db.database.commit()
        cursor.close()
        flash('Cambios guardados exitosamente.')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=4000)
