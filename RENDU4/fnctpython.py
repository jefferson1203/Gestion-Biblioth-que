from datetime import date, timedelta
import matplotlib.pyplot as plt
import psycopg2
conn = psycopg2.connect("dbname ='dbai23a015' user ='ai23a015' host ='tuxa.sme.utc' password ='96ksIv2zQffQ'")
cur = conn.cursor()
sql_file_path = "CREATE_INSERT.sql"

def execute_sql_file():
    # Lire le fichier SQL
    with open(sql_file_path, 'r') as f:
        sql_script = f.read()
        cur.execute(sql_script)
        conn.commit()

def accueil():
    # Connexion à la base de données
    print("\n\n\nBienvenue au service de gestion de la bibliothèque NF18\n")
    print("Veuillez vous connecter en tant que admin ou adhérent\n")
    print("(0) Quitter\n(1) Personnel\n(2) Adhérent\n(3)reset la BD")
    
    choixAccueil = (input("Choisissez 0, 1, 2 ou 3: "))
    if(choixAccueil.isdigit()):
        choixAccueil=int(choixAccueil)
    while choixAccueil != 0:
        mail=''
        if choixAccueil == 1:
            mail=authentification("PERSONNEL")
            if mail!='':
                menuadmin(mail)
        elif choixAccueil == 2:
            mail=authentification("ADHERENT")
            if mail!='':
                menuadherent(mail)
        elif choixAccueil==3:
            execute_sql_file(sql_file_path)
        else:
            print("Saisie invalide, choisissez 0, 1 ou 2: ")
        choixAccueil = (input("Choisissez 0, 1 ou 2: "))
        if(choixAccueil.isdigit()):
            choixAccueil=int(choixAccueil)
    print("Vous avez choisi de quitter\n")

def authentification(type):
    connecte = ''
    print("\n********** Authentification %s **********\n" %(type))
    login = input("Login: ")
    motDebreake = input("Mot de passe: ")
    
    cur.execute("SELECT MEMBRE.Mail FROM %s NATURAL JOIN MEMBRE NATURAL JOIN HISTORIQUE H JOIN COMPTEUTILISATEUR C ON H.login=C.login where C.login='%s' and C.mdp='%s';"  %(type, login, motDebreake))
    resultat = cur.fetchall()
    
    if resultat:
        print("******* Authentification réussie *******\n")
        connecte = resultat[0][0]
    else:
        print("Login ou mot de passe incorrect.")
        
    return connecte

#LES ADMINS
def menuadmin(mail):
    choixmenumembre = 1
    while choixmenumembre != 0:
        print("\n\n\n----Menu Membres %s-----\n" %(mail))
        print("(0) Fermer votre session\n(1) Afficher tous les membres\n(2) Gestion des adherents\n(3) Gestion des ressources\n(4) Statistiques\n------------------")
        choixmenumembre = (input("\n"))
        if(choixmenumembre.isdigit()):
            choixmenumembre=int(choixmenumembre)
        if choixmenumembre == 1:
            sql = "SELECT nom, prenom, mail FROM Membre;;"
            cur.execute(sql)
            result = cur.fetchall()
            for row in result:
                print(row)
                
        elif choixmenumembre == 2:
            ad_menuadmin()
        elif choixmenumembre == 3:
            res_menuadmin()
        elif choixmenumembre == 4:
            stat_menuadmin()
        else:
            print("Saisie invalide, choisissez 0, 1, 2 ou 3: ")
            
    print("Vous avez choisi de revenir a l'accueil\n")

def menuadherent(mail):
    choix=1
    while choix!=0:
        print("\n\n\n----Menu Adhérent  %s-----\n"%(mail))
        print("(0) Revenir au menu principal\n(1) Gestion de mes emprunts\n(2) Rechercher une ressource\n(3) Consulter mes emprunts\n")
        choix = (input("\nSélectionnez une option: "))
        if(choix.isdigit()):
            choix=int(choix)
        if choix == 1:
            gestiondesEmprunts(mail)
        elif choix == 2:
            type =int(input("Je recherche un:\n(1)Livre\n(2)Film\n(3)Musique\n"))
            if type==1:
                recherche("LIVRE")
            elif type==2:
                recherche("FILM")
            elif type==3:
                recherche("MUSIQUE")
        elif choix == 3:
            sql = ("SELECT dateempreinte, duree, etat, ressource, titre, dateapparition, editeur, genre FROM EMPREINTE JOIN EXEMPLAIRE ON EMPREINTE.coderessource=EXEMPLAIRE.idexemplaire JOIN RESSOURCE ON EXEMPLAIRE.ressource=RESSOURCE.code where mailadherent='%s';"%(mail))
            cur.execute(sql)
            result = cur.fetchall()
            for row in result:
                print(row)
        else:
            print("Option invalide, veuillez réessayer.")

def gestiondesEmprunts(mail):
    sql = ("SELECT idexemplaire, dateempreinte, duree, etat, ressource, titre, dateapparition, editeur, genre FROM EMPREINTE JOIN EXEMPLAIRE ON EMPREINTE.coderessource=EXEMPLAIRE.idexemplaire JOIN RESSOURCE ON EXEMPLAIRE.ressource=RESSOURCE.code where mailadherent='%s';"%(mail))
    cur.execute(sql)
    result = cur.fetchall()
    for row in result:
        print(row)
    type=int(input("\n(1)Rendre une ressource\n(2)Emprunter une ressource\n choix: "))
    if(type==1):
        num=int(input("\nNumero de l'exemplaire a rendre: "))
        sql = ("DELETE FROM EMPREINTE WHERE coderessource=%s and mailadherent='%s'"%(num, mail))
        cur.execute(sql)
        if(cur.rowcount>0):
            sql = ("UPDATE EXEMPLAIRE SET DISPONIBLE ='TRUE' where idexemplaire=%s"%(num))
            cur.execute(sql)
        else:
            print("Erreur")
    if(type==2):
        sql = ("SELECT * FROM SANCTION where mailadherent='%s' and datefin>CURRENT_DATE"%(mail))
        cur.execute(sql)
        if(cur.rowcount>0):
            print("Vous ne pouvez pas emprunter vous êtes sanctionner")
        num=(input("\nCode de la ressource a emprunter: "))
        sql = ("SELECT * FROM EXEMPLAIRE where ressource='%s' and disponible='TRUE'"%(num))
        cur.execute(sql)
        if(cur.rowcount>0):
            result=cur.fetchall()
            sql = ("INSERT INTO EMPREINTE VALUES(CURRENT_DATE, '14:00:00', '%s', '%s')"%(num, mail))
            cur.execute(sql)
            sql = ("UPDATE EXEMPLAIRE SET DISPONIBLE='FALSE' WHERE idexemplaire='%s'"%(num))
            cur.execute(sql)
        else:
            print("Pas d'Exemplaire ou de ressource disponible")
    return

def recherche(table):
    print("Rechercher par:\n(1)Titre\n(2)dateDApparition\n(3)Editeur\n(4)Genre\n")
    if(table=="LIVRE"):
        print("(5)Resumer")

    if(table=="FILM"):
        print("(6)Synopsis")
    
    if(table=="MUSIQUE"):
        print("(7)Longeur")
    t = (input("\nChoix: "))
    if(t.isdigit()):
            t=int(t)
    recherche = input("Recherche: ")
    sql = ""
    if t == 1:
        sql = "SELECT * FROM {} NATURAL JOIN RESSOURCE where titre LIKE '%{}%'".format(table, recherche)
    elif t == 2:
        debut="%s-01-01"%(int(recherche))
        fin="%s-01-01"%(int(recherche)+1)
        sql = "SELECT * FROM {} NATURAL JOIN RESSOURCE where dateapparition BETWEEN '{}' AND '{}'".format(table, debut, fin)
    elif t == 3:
        sql = "SELECT * FROM {} NATURAL JOIN RESSOURCE where editeur LIKE '%{}%'".format(table, recherche)
    elif t == 4:
        sql = "SELECT * FROM {} NATURAL JOIN RESSOURCE where genre LIKE '%{}%'".format(table, recherche)
    elif t==5:
        if(table=="LIVRE"):
            sql = "SELECT * FROM {} NATURAL JOIN RESSOURCE where resume LIKE '%{}%'".format(table, recherche)
    elif t==6:
        if(table=="FILM"):
            sql = "SELECT * FROM {} NATURAL JOIN RESSOURCE where synopsis LIKE '%{}%'".format(table, recherche)
    elif t==7:
        if(table=="MUSQIUE"):
            sql = "SELECT * FROM {} NATURAL JOIN RESSOURCE where longueur between {} and {};".format(table, int(recherche)-2, int(recherche)+2)
    cur.execute(sql)
    result = cur.fetchall()
    for row in result:
        print(row)


def ad_menuadmin():
    choix=1
    while choix!=0:
        print("\n\n\n----Gestion des adhérents-----\n")
        print("(0) Revenir au menu principal\n(1) Ajouter un adhérent\n(2) Supprimer un adhérent\n(3) Afficher tous les adhérents\n(4)Changer le mail d'un adhérent\n(5)Creer un compte utilisateur\n(6)ajouter une sanction a un adhérent\n")
        choix = (input("\nSélectionnez une option: "))
        if(choix.isdigit()):
            choix=int(choix)
        if choix == 1:
            mail=input("mail du nouveal adhérent: ")
            cur.execute("SELECT * FROM MEMBRE WHERE mail='%s';"%(mail))
            if(cur.rowcount >0):
                print("Erreur mail déjà associé")
                break
            nom=input("Nom: ")
            prenom=input("Prenom: ")
            adresse=input("Adresse: ")
            dateNaissance=input("Date de Naissance: ")
            tel=input("Tel: ")
            cur.execute("INSERT INTO MEMBRE VALUES('%s', '%s', '%s', '%s', '%s');"%(nom, prenom, adresse, dateNaissance, mail))
            cur.execute("INSERT INTO ADHERENT VALUES('%s', %s);"%(mail, tel))
        elif choix == 2:
            mail=input("mail de l'adhérent: ")
            cur.execute("SELECT * FROM MEMBRE WHERE mail='%s';"%(mail))
            if(cur.rowcount ==0):
                print("Erreur mail pas associé")
                break
            cur.execute("DELETE FROM MEMBRE WHERE mail='%s';"%(mail))
        elif choix == 3:
            sql = "SELECT * FROM ADHERENT NATURAL JOIN MEMBRE;"
            cur.execute(sql)
            result = cur.fetchall()
            for row in result:
                print(row)
        elif choix==4:
            mail=input("mail de l'adhérent: ")
            cur.execute("SELECT * FROM MEMBRE WHERE mail='%s';"%(mail))
            if(cur.rowcount==0):
                print("Erreur mail pas associé")
                break
            nouveaumail=input("mail de l'adhérent: ")
            cur.execute("SELECT * FROM MEMBRE WHERE mail='%s';"%(nouveaumail))
            if(cur.rowcount>0):
                print("Erreur mail déjà associé")
                break
            cur.execute("UPDATE MEMBRE set mail='%s' WHERE mail='%s';"%(nouveaumail, mail))
        elif choix==5:
            mail=input("mail de l'adhérent: ")
            cur.execute("SELECT * FROM MEMBRE WHERE mail='%s';"%(mail))
            if(cur.rowcount==0):
                print("Erreur mail pas associé")
                break
            login=input("Login: ")
            cur.execute("SELECT * FROM COMPTEUTILISATEUR WHERE login='%s';"%(login))
            if(cur.rowcount>0):
                print("Erreur login déjà associé")
                break
            mdp=input("mot de passe")
            cur.execute("INSERT INTO COMPTEUTILISATEUR VALUES('%s', '%s')"%(login, mdp))
            cur.execute("INSERT INTO HISTORIQUE VALUES('%s', '%s', CURRENT_DATE, CURRENT_DATE + INTERVAL '3 years')"%(login, mail))
        elif choix==6:
            mail=input("mail de l'adhérent: ")
            cur.execute("SELECT * FROM MEMBRE WHERE mail='%s';"%(mail))
            if(cur.rowcount==0):
                print("Erreur mail pas associé")
            type=input("La type de sanction: ")
            duree=input("La duree: ")
            cur.execute("INSERT INTO SANCTION VALUES('%s', CURRENT_DATE, CURRENT_DATE + INTERVAL '%s days', '%s');"%(type, duree, mail))
        else:
            print("Option invalide, veuillez réessayer.")



def res_menuadmin():
    while True:
        print("\n\n\n----Gestion des ressources-----\n")
        print("(0) Revenir au menu principal\n(1) Ajouter une ressource\n(2) Modifier une ressource\n(3) Supprimer une ressource\n(4) Afficher toutes les ressources\n(5) ajouter un exemplaire d'une ressource\n(6)afficher tous les exemplaire d'une ressource\n(7) Supprimer un exemplaire\n")
        print("(8)Changer l'etat d'un exemplaire\n(9)Ajouter un contributeur\n(10)liés une ressource\n(11)Liés un contributeur\n(12)Afficher une ressource et ses contributeurs")
        choix = (input("\nSélectionnez une option: "))
        if(choix.isdigit()):
            choix=int(choix)
        
        if choix == 0:
            break
        elif choix == 1:
            code=input("Code de la ressource a ajouter: ")
            titre=input("titre de la ressource a ajouter: ")
            date=input("date de la ressource a ajouter: ")
            editeur=input("editeur de la ressource a ajouter: ")
            genre=input("genre de la ressource a ajouter: ")
            codeDeClassification=input("code de classification de la ressource a ajouter: ")
            sql = ("INSERT INTO RESSOURCE VALUES('%s', '%s', '%s', '%s', '%s', '%s');" %(code, titre, date, editeur, genre, codeDeClassification))
            cur.execute(sql)
            if(cur.rowcount >0):
                print("Ressource ajouter")
            else:
                print("Erreur dans l'ajout\n") 
            break
        elif choix == 2:
            code=input("Code de la ressource a modifier: ")
            sql = ("SELECT * FROM RESSOURCE WHERE code='%s';" %(code))
            cur.execute(sql)
            if(cur.rowcount >0):
                result = cur.fetchall()
                for row in result:
                    print(row)
                type=input("Colonne a Modifier: ")
                nouveau=input("Nouvelle valeur: ")
                sql = ("UPDATE RESSOURCE SET %s='%s'  WHERE code='%s';" %(type, nouveau, code))
                cur.execute(sql)
                if(cur.rowcount >0):
                    print("Modification valider")
                else:
                    print("Type introuvable ou valeur impossible")
            else:
                print("code introuvable\n") 
            break
        elif choix == 3:
            code=input("Code de la ressource a supprimer: ")
            sql = ("DELETE FROM RESSOURCE WHERE code='%s';" %(code))
            cur.execute(sql)
            if(cur.rowcount >0):
                print("Ressource supprimer\n")
            else:
                print("Erreur dans la suppression\n") 
            break
        elif choix == 4:
            sql = "SELECT * FROM RESSOURCE;"
            cur.execute(sql)
            result = cur.fetchall()
            for row in result:
                print(row)
            break
        elif choix == 5:
            code=input("Code de la ressource a laquel ajouter un exemplaire: ")
            sql = ("SELECT * FROM RESSOURCE WHERE code='%s';" %(code))
            cur.execute(sql)
            if(cur.rowcount >0):
                etat = input("Etat de l'Exemplaire: ")
                disponible = input("Disponibilite : ")
                sql = ("INSERT INTO EXEMPLAIRE (etat, disponible, ressource) VALUES('%s', '%s', '%s');" %(etat, disponible, code))
                cur.execute(sql)
                if(cur.rowcount >0):
                    print("Exemplaire creer")
                else:
                    print("Erreur")
        elif choix==6:
                code=input("Code de la ressource: ")
                sql = ("SELECT * FROM RESSOURCE WHERE code='%s';" %(code))
                cur.execute(sql)
                if(cur.rowcount >0):
                    sql = ("SELECT * FROM EXEMPLAIRE WHERE RESSOURCE = '%s';" %(code))
                    cur.execute(sql)
                    result = cur.fetchall()
                    for row in result:
                        print(row)
                else:
                    print("Erreur")
                break
        elif choix == 7:
            code=input("Code de la ressource: ")
            sql = ("SELECT * FROM RESSOURCE WHERE code='%s';" %(code))
            cur.execute(sql)
            if(cur.rowcount >0):
                sql = ("SELECT * FROM EXEMPLAIRE WHERE RESSOURCE = '%s';" %(code))
                cur.execute(sql)
                i=0
                result = cur.fetchall()
                for row in result:
                    i+=1
                    print(row)
                if(i!=0):
                    idExemplaire=input("Id de l'exmplaire a surppimer")
                    sql=("DELETE FROM EXEMPLAIRE WHERE idexemplaire=%s" %(idExemplaire))
                    cur.execute(sql)
                    if(cur.rowcount >0):
                        print("Exemplaire supprimer")
                    else:
                        print("Erreur")
            else:
                print("Erreur")
            break
        elif(choix==8):
            code=input("Code de la ressource: ")
            sql = ("SELECT * FROM RESSOURCE WHERE code='%s';" %(code))
            cur.execute(sql)
            if(cur.rowcount >0):
                sql = ("SELECT * FROM EXEMPLAIRE WHERE RESSOURCE = '%s';" %(code))
                cur.execute(sql)
                i=0
                result = cur.fetchall()
                for row in result:
                    i+=1
                    print(row)
                if(i!=0):
                    idExemplaire=input("Id de l'exmplaire a modifier")
                    sql=("SELECT * FROM EXEMPLAIRE WHERE idexemplaire=%s" %(idExemplaire))
                    cur.execute(sql)
                    if(cur.rowcount >0):
                        etat = input("nouvel etat: ")
                        sql=("UPDATE EXEMPLAIRE SET ETAT='%s' WHERE idexemplaire=%s" %(etat, idExemplaire))
                        cur.execute(sql)
                        if(cur.rowcount >0):
                            print("Exemplaire modifier")
                        else:
                            print("Erreur")
                    else:
                        print("Erreur")
            else:
                print("Erreur")
            break
        elif choix==9:
            sql = ("SELECT * FROM CONTRIBUTEUR;")
            cur.execute(sql)
            result = cur.fetchall()
            for row in result:
                    print(row)
            id=input("Id: ")
            nom=input("Nom: ")
            prenom=input("Prenom: ")
            dateDeNaissance=input("Date de Naissance: ")
            Nationalite=input("Nationalité: ")
            
            sql = ("INSERT INTO CONTRIBUTEUR VALUES('%s', '%s', '%s', '%s', '%s');" %(id, nom, prenom, dateDeNaissance, Nationalite))
            cur.execute(sql)
            if(cur.rowcount ==0):
                print("Erreur")
            else:
                print("Success")
            break
        elif choix==10:
            code=input("Code de la ressource: ")
            sql = ("SELECT * FROM RESSOURCE WHERE code='%s';" %(code))
            cur.execute(sql)
            if(cur.rowcount ==0):
                break
            print("Ressource ajouter\n")
            type=(input("Selectionner : \n(1)Livre\n (2)Musique\n (3)Film\n"))
            if(type.isdigit()):
                type=int(type)
            if(type==1):
                isbn=input("ISBN: ")
                resumer=input("Resumer: ")
                langue=input("Langue: ")
                sql=("INSERT INTO INTO LIVRE VALUES('%s', '%s', '%s', '%s');" %(code, isbn, resumer, langue))
                cur.execute(sql)
                if(cur.rowcount ==0):
                    print("Erreur")
            elif(type==2):
                longeur=input("longeur: ")
                synopsis=input("synopsis: ")
                langue=input("Langue: ")
                sql=("INSERT INTO INTO FILM VALUES('%s', '%s', %s, '%s');" %(code, langue, longeur, synopsis))
                cur.execute(sql)
                if(cur.rowcount ==0):
                    print("Erreur")
            elif(type==3):
                longeur=input("longeur: ")
                sql=("INSERT INTO INTO MUSIQUE VALUES('%s', %s);" %(code, longeur))
                cur.execute(sql)
                if(cur.rowcount ==0):
                    print("Erreur")
            else:
                print("Erreur, ressource supprimer")
                sql=("DELETE FROM RESSOURCE WHERE code='%s"%(code))
                cur.execute()
            break
        elif choix==11:
            sql = ("SELECT * FROM CONTRIBUTEUR;")
            cur.execute(sql)
            result = cur.fetchall()
            for row in result:
                print(row)
            code=input("Code de la ressource: ")
            sql = ("SELECT * FROM RESSOURCE WHERE code='%s';" %(code))
            cur.execute(sql)
            if(cur.rowcount ==0):
                break
            type=(input("Selectionner : \n(1)Livre\n (2)Musique\n (3)Film\n"))
            if(type.isdigit()):
                type=int(type)
            if(type==1):
                sql = ("SELECT * FROM LIVRE WHERE code='%s';" %(code))
                cur.execute(sql)
                if(cur.rowcount ==0):
                    break
                auteur=input("Auteur: ")
                sql = ("INSERT INTO AUTEUR VALUES ('%s', '%s');" %(auteur, code))
                cur.execute(sql)
                if(cur.rowcount ==0):
                    print("Erreur")
            elif(type==2):
                sql = ("SELECT * FROM FILM WHERE code='%s';" %(code))
                cur.execute(sql)
                if(cur.rowcount ==0):
                    break
                type=input("(1) Acteur\n (2)Realisateur\n")
                if(type==1):
                    acteur=input("Acteur: ")
                    sql = ("INSERT INTO ACTEUR VALUES ('%s', '%s');" %(acteur, code))
                elif type==2:
                    realisateur=input("Realisateur: ")
                    sql = ("INSERT INTO REALISATEUR VALUES ('%s', '%s');" %(realisateur, code))
                cur.execute(sql)
                if(cur.rowcount ==0):
                    print("Erreur")
            elif(type==3):
                sql = ("SELECT * FROM MUSIQUE WHERE code='%s';" %(code))
                cur.execute(sql)
                if(cur.rowcount ==0):
                    break
                type=input("(1)Compositeur\n (2)interprete\n")
                if(type==1):
                    compo=input("Compositeur: ")
                    sql = ("INSERT INTO COMPOSITEUR VALUES ('%s', '%s');" %(compo, code))
                elif type==2:
                    interprete=input("Interprete: ")
                    sql = ("INSERT INTO INTERPRETE VALUES ('%s', '%s');" %(interprete, code))
                cur.execute(sql)
                if(cur.rowcount ==0):
                    print("Erreur")
        elif choix==12:
            code=input("Code de la ressource: ")
            sql = ("SELECT * FROM RESSOURCE WHERE code='%s';" %(code))
            cur.execute(sql)
            if(cur.rowcount ==0):
                break
            print("Ressource ajouter\n")
            type=int(input("Selectionner : \n(1)Livre\n (2)Musique\n (3)Film\n"))
            if(type==1):
                sql = ("SELECT * FROM LIVRE WHERE code='%s';" %(code))
                cur.execute(sql)
                result = cur.fetchall()
                for row in result:
                    print(row)
                    print("\nAuteur:\n")
                    sql = ("SELECT C.nom, C.prenom FROM CONTRIBUTEUR C JOIN AUTEUR R ON C.idcontributeur=R.contributeur where code='%s';" %(code))
                    cur.execute(sql)
                    result2 = cur.fetchall()
                    for row2 in result2:
                        print(row2)
            elif type==2:
                sql = ("SELECT * FROM FILM WHERE code='%s';" %(code))
                cur.execute(sql)
                result = cur.fetchall()
                for row in result:
                    print(row)
                    print("\nActeur:\n")
                    sql = ("SELECT C.nom, C.prenom FROM CONTRIBUTEUR C JOIN ACTEUR R ON C.idcontributeur=R.contributeur where code='%s';" %(code))
                    cur.execute(sql)
                    result2 = cur.fetchall()
                    for row2 in result2:
                        print(row2)
                    print("\nREALISATEUR:\n")
                    sql = ("SELECT C.nom, C.prenom FROM CONTRIBUTEUR C JOIN REALISATEUR R ON C.idcontributeur=R.contributeur where code='%s';" %(code))
                    cur.execute(sql)
                    result2 = cur.fetchall()
                    for row2 in result2:
                        print(row2)
            elif type==3:
                sql = ("SELECT * FROM MUSIQUE WHERE code='%s';" %(code))
                cur.execute(sql)
                result = cur.fetchall()
                for row in result:
                    print(row)
                    print("\nCompositeur:\n")
                    sql = ("SELECT C.nom, C.prenom FROM CONTRIBUTEUR C JOIN COMPOSITEUR R ON C.idcontributeur=R.contributeur where code='%s';" %(code))
                    cur.execute(sql)
                    result2 = cur.fetchall()
                    for row2 in result2:
                        print(row2)
                    print("\nInterprete:\n")
                    sql = ("SELECT C.nom, C.prenom FROM CONTRIBUTEUR C JOIN INTERPRETE R ON C.idcontributeur=R.contributeur where code='%s';" %(code))
                    cur.execute(sql)
                    result2 = cur.fetchall()
                    for row2 in result2:
                        print(row2)
        else:
            print("Option invalide, veuillez réessayer.")


def stat_menuadmin():
    choix=1
    while choix!=0:
        print("\n\n\n----Statistiques-----\n")
        print("(0) Revenir au menu principal\n(1) Afficher la ressource la plus empruntée\n(2) Liste des ressources les plus populaires\n")
        choix = (input("\nSélectionnez une option: "))
        if(choix.isdigit()):
            choix=int(choix)
        if choix == 0:
            break
        elif choix == 1:
            sql=("SELECT RESSOURCE.code, COUNT(POPULARITE.code) as total, RESSOURCE.titre, RESSOURCE.dateapparition, RESSOURCE.genre, RESSOURCE.editeur FROM POPULARITE JOIN RESSOURCE ON POPULARITE.code = RESSOURCE.code GROUP BY RESSOURCE.code ORDER BY total DESC LIMIT 1")
            cur.execute(sql)
            result2 = cur.fetchall()
            for row2 in result2:
                print(row2)
            break
        elif choix == 2:
            sql=("SELECT RESSOURCE.code, COUNT(POPULARITE.code) as total, RESSOURCE.titre, RESSOURCE.dateapparition, RESSOURCE.genre, RESSOURCE.editeur FROM POPULARITE JOIN RESSOURCE ON POPULARITE.code = RESSOURCE.code GROUP BY RESSOURCE.code ORDER BY total DESC LIMIT 1")
            cur.execute(sql)
            result2 = cur.fetchall()
            for row2 in result2:
                print(row2)
            break
        else:
            print("Option invalide, veuillez réessayer.")



accueil()
conn.commit()
cur.close()
conn.close()