#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <fstream>
#include <iostream>
#include <string>
#include <vector>
static PyObject *K1Error;

static PyObject *k1a_system(PyObject *self, PyObject *args) {
    const char *command;
    int sts;

    if (!PyArg_ParseTuple(args, "s", &command)) return NULL;
    sts = system(command);
    if (sts < 0) {
        PyErr_SetString(K1Error, "System command failed");
        return NULL;
    }
    return PyLong_FromLong(sts);
}

void print(std::string s) {
    std::ofstream f;
    f.open("/home/kelvin/repos/labs/k1a/logs.txt", std::ios_base::app);
    f << s;
    f.close();
}

void println(std::string s) { print(s + "\n"); }

void clear() {
    std::ofstream f;
    f.open("/home/kelvin/repos/labs/k1a/logs.txt");
    f << "";
    f.close();
}

static PyObject *k1a_clear(PyObject *self, PyObject *args) {
    clear();
    Py_RETURN_NONE;
}

static PyObject *k1a_test(PyObject *self, PyObject *args) {
    const char *str;
    if (!PyArg_ParseTuple(args, "s", &str)) return NULL;
    const std::string a = str;
    // return PyUnicode_FromString("def");
    return PyUnicode_FromString((a + "end").c_str());
}

static PyObject *k1a_str_split(PyObject *self, PyObject *args) {
    char *_str, *_delim, *str, *begin;
    if (!PyArg_ParseTuple(args, "ss", &_str, &_delim)) return NULL;
    char delim = _delim[0], quoteChar = '"';

    begin = str = (char *)malloc((strlen(_str) + 1) * sizeof(char));
    strcpy(str, _str);
    PyObject *plist = PyList_New(0);

    int i = 0;
    bool inBlock = false;

    while (str[i] != NULL) {
        char a = str[i];
        if (a == delim && !inBlock) {
            str[i] = NULL;
            PyList_Append(plist, PyUnicode_FromString(begin));
            begin = str + (i + 1);
        } else if (!inBlock && (a == '"' || a == '\'')) {  // new block
            inBlock = true;
            quoteChar = a;
        } else if (inBlock && a == quoteChar)
            inBlock = false;  // exiting block
        i++;
    }
    PyList_Append(plist, PyUnicode_FromString(begin));
    free(str);
    return plist;
}

static PyObject *k1a_str_split2(PyObject *self, PyObject *args) {
    char *_str, *_delim, *str, *begin;
    if (!PyArg_ParseTuple(args, "ss", &_str, &_delim)) return NULL;
    char delim = _delim[0], quoteChar = '"';

    begin = str = (char *)malloc((strlen(_str) + 1) * sizeof(char));
    strcpy(str, _str);
    PyObject *plist = PyList_New(0);

    int i = 0;

    while (str[i] != NULL) {
        char a = str[i];
        if (a == delim) {
            str[i] = NULL;
            PyList_Append(plist, PyUnicode_FromString(begin));
            begin = str + (i + 1);
        }
        i++;
    }
    PyList_Append(plist, PyUnicode_FromString(begin));
    free(str);
    return plist;
}

static PyMethodDef K1aMethods[] = {
    {"system", k1a_system, METH_VARARGS, "Execute a shell command."},
    {"test", k1a_test, METH_VARARGS,
     "Test function for developing the library"},
    {"clear", k1a_clear, METH_VARARGS, "Clear logs"},
    {"str_split", k1a_str_split, METH_VARARGS,
     "Splits string into multiple fragments using a delimiter, respecting "
     "quotes"},
    {"str_split2", k1a_str_split2, METH_VARARGS,
     "Splits string into multiple fragments using a delimiter, respecting "
     "quotes"},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

static struct PyModuleDef k1amodule = {
    PyModuleDef_HEAD_INIT, "k1a", /* name of module */
    NULL,                         /* module documentation, may be NULL */
    -1, /* size of per-interpreter state of the module,
           or -1 if the module keeps state in global variables. */
    K1aMethods};

extern "C" {
PyMODINIT_FUNC PyInit_k1a(void) {
    PyObject *m;

    m = PyModule_Create(&k1amodule);
    if (m == NULL) return NULL;

    K1Error = PyErr_NewException("k1a.error", NULL, NULL);
    Py_XINCREF(K1Error);
    if (PyModule_AddObject(m, "error", K1Error) < 0) {
        Py_XDECREF(K1Error);
        Py_CLEAR(K1Error);
        Py_DECREF(m);
        return NULL;
    }
    char *version = "1.0.1";
    if (PyModule_AddObject(m, "__version__", PyUnicode_FromString(version)) <
        0) {
        Py_DECREF(m);
        return NULL;
    }

    return m;
}
}
