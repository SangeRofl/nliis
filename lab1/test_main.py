import pytest
import sqlite3
from main import SearchModel
from sklearn.metrics import precision_recall_curve
import matplotlib.pyplot as plt


db_docs_conn = sqlite3.connect(r'test-docs.db')
db_docs_cur = db_docs_conn.cursor()


test_data = [
        ('Document1', 'apple', '2023-11-23'),
        ('Document2', 'cucumber', '2023-11-23'),
        ('Document3', '', '2023-11-23'),
        ('Document4', 'apple cucumber', '2023-11-23'),
        ('Document5', 'avocado', '2023-11-23'),
        ('Document6', 'avocado cucumber', '2023-11-23'),
        ('Document7', 'avocado cucumber apple', '2023-11-23')
    ]


@pytest.fixture(scope='session', autouse=True)
def setup_test_data(request):
    db_docs_cur.execute("""
    CREATE TABLE IF NOT EXISTS docs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        content TEXT,
        date TEXT);
    """)
    db_docs_conn.commit()
    db_docs_cur.execute("SELECT * FROM docs;")
    
    for data in test_data:
        db_docs_cur.execute("INSERT INTO docs (name, content, date) VALUES (?, ?, ?);", data)
    db_docs_conn.commit()

    def fin():
        db_docs_cur.execute("DROP TABLE IF EXISTS docs;")
        db_docs_conn.commit()
        
    request.addfinalizer(fin)
    

def test_fixture():
    db_docs_cur.execute("SELECT * FROM docs;")
    assert len(db_docs_cur.fetchall()) == 7
        

def test_r():
    search_word = 'apple'
    s = SearchModel()
    s.db_docs_conn = sqlite3.connect(r'test-docs.db')
    s.db_docs_cur = db_docs_conn.cursor()
    result = s._search_word_in_docs(search_word)
    assert len(result) == 3
    r = len(result) / 3
    assert r == 1 

def test_p():
    search_word = 'cucumber'
    s = SearchModel()
    s.db_docs_conn = sqlite3.connect(r'test-docs.db')
    s.db_docs_cur = db_docs_conn.cursor()
    result = s._search_word_in_docs(search_word)
    assert len(result) == 4
    p = 4 / len(result)
    assert p == 1 


def test_a():
    search_word = 'avocado'
    s = SearchModel()
    s.db_docs_conn = sqlite3.connect(r'test-docs.db')
    s.db_docs_cur = db_docs_conn.cursor()
    result = s._search_word_in_docs(search_word)
    assert len(result) == 3
    a = (len(result) + (len(test_data) - len(result))) / len(test_data)
    assert a == 1 


def test_e():
    search_word = 'apple'
    s = SearchModel()
    s.db_docs_conn = sqlite3.connect(r'test-docs.db')
    s.db_docs_cur = db_docs_conn.cursor()
    result = s._search_word_in_docs(search_word)
    assert len(result) == 3
    a = (len(result) - 3) / len(test_data)
    assert a == 0


def test_f():
    search_word = 'cucumber'
    s = SearchModel()
    s.db_docs_conn = sqlite3.connect(r'test-docs.db')
    s.db_docs_cur = db_docs_conn.cursor()
    result = s._search_word_in_docs(search_word)
    assert len(result) == 4
    r = len(result) / 4
    p = 4 / len(result)
    f = 2 / (1 / p + 1 / r)
    assert f == 1


def test_11():
    search_word = 'cucumber'
    s = SearchModel()
    s.db_docs_conn = sqlite3.connect(r'test-docs.db')
    s.db_docs_cur = db_docs_conn.cursor()
    result = s._search_word_in_docs(search_word)
    y_true = [True, True, True, True]
    expected = [2,4,6,7]
    y_scores = [result[i] == expected[i] for i in range(len(result))]
    precision, recall, thresholds = precision_recall_curve(y_true, y_scores)

    plt.plot(recall, precision, marker='.')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('11-Point Precision-Recall Curve')
    plt.show()