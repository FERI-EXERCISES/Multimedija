#include <iostream>
#include <cstdlib>   // For rand() and srand()
#include <vector>
#include <ctime>
#include <bitset>
#include <unordered_map>
#include <algorithm>
#include <chrono>

static std::unordered_map<int, std::string> DICTIONARY_ENCODE = {
        {0,   ""},

        {-2,  "00"},
        {-1,  "01"},
        {1,   "10"},
        {2,   "11"},

        {-6,  "000"},
        {-5,  "001"},
        {-4,  "010"},
        {-3,  "011"},
        {3,   "100"},
        {4,   "101"},
        {5,   "110"},
        {6,   "111"},

        {-14, "0000"},
        {-13, "0001"},
        {-12, "0010"},
        {-11, "0011"},
        {-10, "0100"},
        {-9,  "0101"},
        {-8,  "0110"},
        {-7,  "0111"},
        {7,   "1000"},
        {8,   "1001"},
        {9,   "1010"},
        {10,  "1011"},
        {11,  "1100"},
        {12,  "1101"},
        {13,  "1110"},
        {14,  "1111"},

        {-30, "00000"},
        {-29, "00001"},
        {-28, "00010"},
        {-27, "00011"},
        {-26, "00100"},
        {-25, "00101"},
        {-24, "00110"},
        {-23, "00111"},
        {-22, "01000"},
        {-21, "01001"},
        {-20, "01010"},
        {-19, "01011"},
        {-18, "01100"},
        {-17, "01101"},
        {-16, "01110"},
        {-15, "01111"},
        {15,  "10000"},
        {16,  "10001"},
        {17,  "10010"},
        {18,  "10011"},
        {19,  "10100"},
        {20,  "10101"},
        {21,  "10110"},
        {22,  "10111"},
        {23,  "11000"},
        {24,  "11001"},
        {25,  "11010"},
        {26,  "11011"},
        {27,  "11100"},
        {28,  "11101"},
        {29,  "11110"},
        {30,  "11111"}
};

static std::unordered_map<std::string, int> DICTIONARY_DECODE = {
        {"", 0},

        {"00",  -2},
        {"01",  -1},
        {"10",  1},
        {"11",  2},

        {"000", -6},
        {"001", -5},
        {"010", -4},
        {"011", -3},
        {"100", 3},
        {"101", 4},
        {"110", 5},
        {"111", 6},

        {"0000", -14},
        {"0001", -13},
        {"0010", -12},
        {"0011", -11},
        {"0100", -10},
        {"0101", -9},
        {"0110", -8},
        {"0111", -7},
        {"1000", 7 },
        {"1001", 8 },
        {"1010", 9 },
        {"1011", 10},
        {"1100", 11},
        {"1101", 12},
        {"1110", 13},
        {"1111", 14},

        {"00000", -30},
        {"00001", -29},
        {"00010", -28},
        {"00011", -27},
        {"00100", -26},
        {"00101", -25},
        {"00110", -24},
        {"00111", -23},
        {"01000", -22},
        {"01001", -21},
        {"01010", -20},
        {"01011", -19},
        {"01100", -18},
        {"01101", -17},
        {"01110", -16},
        {"01111", -15},
        {"10000", 15},
        {"10001", 16},
        {"10010", 17},
        {"10011", 18},
        {"10100", 19},
        {"10101", 20},
        {"10110", 21},
        {"10111", 22},
        {"11000", 23},
        {"11001", 24},
        {"11010", 25},
        {"11011", 26},
        {"11100", 27},
        {"11101", 28},
        {"11110", 29},
        {"11111", 30}
};

std::string handleNumber(int num) {
    if (abs(num) > 0 && abs(num) < 3) //00
        return " 00 " + DICTIONARY_ENCODE[num];
    else if (abs(num) > 2 && abs(num) < 7) //01
        return " 01 " + DICTIONARY_ENCODE[num];
    else if (abs(num) > 6 && abs(num) < 15) //10
        return " 10 " + DICTIONARY_ENCODE[num];
    else if (abs(num) > 14 && abs(num) < 31) //11
        return " 11 " + DICTIONARY_ENCODE[num];
    return "";
}

std::string compress(const std::vector<int> &diff) {
    std::string result = std::bitset<8>(diff[0]).to_string();
    int counter;

    //std::cout << std::bitset<8>(43).to_string() << std::endl;
    for (int i = 1; i < diff.size(); ++i) {
        //ponovitve
        if(diff[i] == 0){
            counter = 0;
            for (int j = i + 1; j < diff.size() && j < i + 8; ++j) {
                if (diff[i] == diff[j])
                    counter++;
                else
                    break;
            }
            if (counter != 0) { // vec krat 0
                result += " 01 " + std::bitset<3>(counter).to_string();
                i += counter;
                continue;
            } else { // samo 1 nicla
                result += " 01 000";
                continue;
            }

        }


        if (abs(diff[i]) > 30) { //absolutno kodiranje (10)
            if (diff[i] > 0)
                result += " 10 0";
            else
                result += " 10 1";

            result += std::bitset<8>(abs(diff[i])).to_string();

            continue;
        }

        result += " 00" + handleNumber(diff[i]); //Razlika (00)
    }
    result += " 11"; //Konec (11)

    return result;
}

std::vector<int> decompress(const std::string& code){
    std::vector<int> result;

    std::string str = code;

    //static 8 bits always
    int number = stoi(code.substr(0,8), 0, 2);
    result.push_back(number);

    int i;
    for (i = 9; i < code.length(); ++i) { //povsod -1 i na koncu ker ++i (:P)
        std::string opcode = code.substr(i, 2);
        i += 3;

        if (opcode == "00"){
            std::string numberCode = code.substr(i, 2);
            i += 3;
            if (numberCode == "00"){
                //number = stoi(code.substr(15, 2), 0, 2);
                number = DICTIONARY_DECODE[code.substr(i, 2)];
                i += 2;
            } else if (numberCode == "01"){
                //number = std::stoi(code.substr(15, 3), 0, 2);
                number = DICTIONARY_DECODE[code.substr(i, 3)];
                i += 3;
            } else if (numberCode == "10"){
                //number = std::stoi(code.substr(15, 4));
                number = DICTIONARY_DECODE[code.substr(i, 4)];
                i += 4;
            } else if (numberCode == "11"){
                //number = std::stoi(code.substr(15, 5));
                number = DICTIONARY_DECODE[code.substr(i, 5)];
                i += 5;
            } else {
                std::cout << "Napaka pri branju kode" << std::endl;
            }
            result.push_back(number);
        }else if(opcode == "01"){
            number = std::stoi(code.substr(i, 3), 0, 2);
            i += 3;
            for (int j = 0; j <= number; ++j) {
                result.push_back(0);
            }
        } else if(opcode == "10"){
            if(code.substr(i, 1) == "0"){
                number = std::stoi(code.substr(i+1, 8), 0, 2);
            }else{
                number = -std::stoi(code.substr(i+1, 8), 0, 2);
            }
            i += 9;
            result.push_back(number);
        } else if(opcode == "11"){
            break;
        } else {
            std::cout << "Napaka pri branju kode" << std::endl;
        }
    }
    return result;
}


std::vector<int> getRandomVec0To255(int size) {
    std::vector<int> vector;
    vector.reserve(size);

    for (int i = 0; i < size; i++) {
        vector.push_back(rand() % 256);
    }

    return vector;
}

std::vector<int> getRandomVecDifference0ToM(int size, int M) {
    std::vector<int> vector;
    vector.reserve(size);
    int tmp;

    vector.push_back(rand() % 256); // First element is random (0-255)
    for (int i = 1; i < size; i++) {
        tmp = rand() % (2 * M + 1) - M;
        if (((vector[i - 1] + tmp) > 255) || ((vector[i - 1] + tmp) < 0))
            vector.push_back(vector[i - 1] - tmp);
        else
            vector.push_back(vector[i - 1] + tmp);
    }

    return vector;
}

std::vector<int> getDiffs(const std::vector<int> &vector) {
    std::vector<int> diff;
    diff.reserve(vector.size());
    diff.push_back(vector[0]);

    for (int i = 1; i < vector.size(); i++) {
        diff.push_back(vector[i] - vector[i - 1]);
    }

    return diff;
}

std::vector<int> removeDiffs(const std::vector<int> &diff) {
    std::vector<int> vector;
    vector.reserve(diff.size());
    vector.push_back(diff[0]);

    for (int i = 1; i < diff.size(); i++) {
        vector.push_back(vector[i - 1] + diff[i]);
    }

    return vector;
}

void printVector(const std::vector<int> &vector) {
    for (int i: vector) {
        std::cout << i << " ";
    }
    std::cout << std::endl;
}

void formattedOutput(const std::vector<int> &vec){
    std::vector<int> diff = getDiffs(vec);

    auto start{std::chrono::steady_clock::now()};
    std::string compresed = compress(diff);
    auto end{std::chrono::steady_clock::now()};
    std::chrono::duration<double> CompressTime{end - start};

    std::string clean = compresed;

    clean.erase(std::remove_if(clean.begin(), clean.end(), ::isspace), clean.end());

    start = std::chrono::steady_clock::now();
    std::vector<int> decompressed = decompress(compresed);
    end = std::chrono::steady_clock::now();
    std::chrono::duration<double> DecompressTime{end - start};

    std::vector<int> output = removeDiffs(decompressed);

    for (int i = 0; i < output.size(); ++i) {
        if(output[i] != vec[i]){
            std::cout << "ERROR!" << std::endl;
            return;
        }
    }

    //printVector(vec);
    //std::cout << compresed << std::endl;
    std::cout << "Size diff: " << vec.size()*8 << " vs " << clean.size()-1 << std::endl;
    std::cout << "Compression: " << CompressTime << " Decompression: " << DecompressTime << std::endl;

    std::cout << std::endl; //--------------------------------
}

int main() {
    // Seed the random number generator with the current time
    srand(static_cast<unsigned int>(std::time(nullptr)));

    std::vector<int> N = {5, 50, 500, 5000, 50000};
    std::vector<int> M = {5, 10, 15, 30};

    std::vector<int> vec, diff, decompressed;
    std::string compresed;

    for (int i = 0; i < 5; ++i) {
        vec = getRandomVec0To255(N[i]);
        std::cout << "Size: " << N[i] << std::endl;
        formattedOutput(vec);
        for (int j = 0; j < 4; ++j) {
            vec = getRandomVecDifference0ToM(N[i], M[j]);
            std::cout << "Size: " << N[i] << " Diff: " << M[j] << std::endl;
            formattedOutput(vec);
        }
    }

    std::cout << "-----------------------------------" << std::endl;

    std::vector<int> Input = {55, 53, 53, 53, 53, 53, 10, 10, 11, 11, 11, 11};
    printVector(Input);
    diff = getDiffs(Input);
    printVector(diff);
    compresed = compress(diff);
    std::cout << compresed << std::endl;
    decompressed = decompress(compresed);
    printVector(decompressed);
    vec = removeDiffs(decompressed);
    printVector(vec);

    return 0;
}
