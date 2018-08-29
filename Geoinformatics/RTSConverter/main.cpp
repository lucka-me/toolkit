/*********************************** ABOUT ************************************/
/* RTS Converter                                                              */
/* Author:  Lucka                                                             */
/* Version: 0.1                                                               */
/* Licence: MIT                                                               */
/******************************** DECLARATION *********************************/
#include <iostream>
#include <iomanip>
#include <fstream>
#include <sstream>

using namespace std;

string to_string(double number, int precision);
void replaceString(string &line, string target, string str);

/************************************ MAIN ************************************/
int main(int argc, char const *argv[]) {
	fstream inputFile, outputFile;
    string inputFileName, outputFileName;

    char command;
    cout << "Enter the RTS filename (including suffix, \"SOURCE.RTS\" for default): ";
    getline(cin, inputFileName);
    inputFileName = inputFileName == "" ? "SOURCE.RTS" : inputFileName;
    while (inputFileName.rfind(".RTS") == string::npos) {
        cout << "The suffix \".RTS\" is NOT found, are you sure to continue? [Y/N]: ";
        cin >> command;
        if (command == 'Y' || command == 'y') {
            break;
        }
        cin.ignore(2, '\n');
        cout << "Please enter the filename again: ";
        getline(cin, inputFileName);
    }
    cout << "Enter the DAT filename (including suffix, \"TARGET.DAT\" for default): ";
    getline(cin, outputFileName);
    outputFileName = outputFileName == "" ? "TARGET.DAT" : outputFileName;

    inputFile.open(inputFileName, ios::in);
    outputFile.open(outputFileName, ios::out);

    string headLine;
    for (int line = 0; line < 7; line++) {
        getline(inputFile, headLine);
    }

    string lineString;
    int counter = 0;
    char type1;
    string type2;
    string pointName;
    double pointX, pointY, pointZ;
    string abandonedString;
    double abandonedNumber;
    while (!inputFile.eof()) {
        counter++;
        stringstream lineStringStream;
        getline(inputFile, lineString);
        if(inputFile.eof()) break;
        replaceString(lineString, " ", "");
        replaceString(lineString, ",", " ");
        lineStringStream << lineString;
        lineStringStream >> type1 >> type2 >> pointName
                         >> abandonedNumber >> abandonedNumber >> abandonedNumber
                         >> pointX >> pointY >> pointZ
                         >> abandonedNumber >> abandonedNumber >> abandonedString;
        if (type1 == 'X'  ||
            type2 == "NT" ||
            type2 == "ST" ||
            type2 == "BS") {
            counter--;
            continue;
        }
        cout << pointName << ": ("
             << to_string(pointX, 4) << ", "
             << to_string(pointY, 4) << ", "
             << to_string(pointZ, 4) << ")."
             << endl;
        outputFile << pointName << ",,"
                   << to_string(pointY, 4) << ","
                   << to_string(pointX, 4) << ","
                   << to_string(pointZ, 4) << endl;
    }
    cout << "Converted " << counter << " points." << endl;
	return 0;
}

/********************************* FUNCTION  **********************************/
string to_string(double number, int precision) {
    stringstream tempStringStream;
    string result;
    // The "fixed" converts the float point number to fixed point number
    // setprecision() sets the precision of:
    // fixed and scientific -> after decimal point
    // other -> the whole number
    tempStringStream << fixed << setprecision(precision) << number;
    tempStringStream >> result;
    return result;
}

void replaceString(string &line, const string target, const string str) {
    string::size_type position = 0;
	string::size_type lengthTarget = target.size();
	string::size_type lengthStr = str.size();
	while((position = line.find(target, position)) != string::npos)
	{
		line.replace(position, lengthTarget, str);
		position += lengthTarget;
	}
}
