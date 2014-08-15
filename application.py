from flask import Flask, jsonify, request
import _mysql, sys

DB_ADDRESS = "masterpieceproject.ckzqvcs35gsd.us-west-2.rds.amazonaws.com"
DB_USER = 'rhandy87'
DB_PASSWORD = 'raph1027'
DB_NAME = 'masterpiece'

app = Flask(__name__)
db = _mysql.connect(DB_ADDRESS, DB_USER, DB_PASSWORD, DB_NAME)

app.config.update(
DEBUG=True
)

@app.route('/')
def test():
    return "Test Connection Successful"

@app.route('/get_user/<username>')
def return_user_info(username):
    return_info = {}
    db.query("SELECT * FROM %s.users WHERE user_name = '%s'" % (DB_NAME,username))
    r = db.store_result()
    try:
        info = r.fetch_row()[0]
    except:
        return_info['error'] = 'No such user'
        return jsonify(return_info)
    return_info['user_id'] = info[0]
    return_info['user_name'] = info[1]
    return jsonify(return_info)

@app.route('/create_user/<username>')
def create_user(username):
    result = {}
    try:
        db.query("INSERT INTO %s.users (user_name) VALUES ('%s')" % (DB_NAME,username))
        result['status'] = "Success"
    except:
        result['error'] = sys.exc_info()[1]
    return jsonify(result)

@app.route('/delete_user/<username>')
def delete_user(username):
    result = {}
    try:
        db.query("DELETE FROM %s.users WHERE user_name='%s'" % (DB_NAME,username))
        result['status'] = "Success"
    except:
        result['error'] = sys.exc_info()[1]
    return jsonify(result)    

@app.route('/set_high_score/<username>/<int:score>')
def set_high_score(username, score):
    high_score=score
    db.query("SELECT s.high_score FROM %s.high_scores s INNER JOIN %s.users u ON s.user_id = u.user_id WHERE u.user_name = '%s'" % (DB_NAME,DB_NAME,username))
    r = db.store_result()
    try:
        info = r.fetch_row()[0]
        print "\n\nOld score: %d\tNew score: %d\n\n" % (int(info[0]), high_score)
        high_score = int(info[0])
        if high_score > score:
            print "\n\nOld score %d > New Score %d\n\n" % (high_score, score)
        else:
            high_score = score
    except:
        high_score = score
        print sys.exc_info()
    print "The current high score is %d" % high_score
    result = {}
    try:
        db.query("INSERT INTO %s.high_scores (user_id,high_score) SELECT user_id, %d FROM %s.users WHERE user_name = '%s' ON DUPLICATE KEY UPDATE user_id=VALUES(user_id), high_score=VALUES(high_score)" % (DB_NAME,high_score,DB_NAME,username))
        result['status'] = 'Success'
    except:
        result['error'] = "Error: %s" % str(sys.exc_info())
    return jsonify(result)

@app.route('/get_high_score/<username>')
def get_high_score(username):
    return_info = {}
    db.query("SELECT s.high_score FROM %s.high_scores s INNER JOIN %s.users u ON s.user_id = u.user_id WHERE u.user_name = '%s'" % (DB_NAME,DB_NAME,username))
    r = db.store_result()
    try:
        info = r.fetch_row()[0]
    except:
        return_info['error'] = 'No high score for %s' % username
        return jsonify(return_info)
    return jsonify(high_score=info[0])



if __name__ == '__main__':
    app.run(host='0.0.0.0')
