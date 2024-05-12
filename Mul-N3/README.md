# Vaja 3 - Kompresija zvoka

V poljubnem programskem jeziku izdelajte aplikacijo, ki bo omogočila odpiranje nekompresiranih zvočnih posnetkov tipa WAV in kompresijo stereo kanalov z algoritmom MDCT. Pri tem se osredotočite na 16-bitne vzorce (ang. sample).

Za branje/zapisovanje WAV datotek lahko uporabite poljubno knjižico (npr. WaveFileReader od NAudio za C#, SoundFileRead od SoundFile++ za C++).

Uporabniku naj bo omogočeno sledeče:

Izbira vhodne nekompresirane zvočne datoteke tipa WAV.
Faktor stiskanja (parameter M) in velikost bloka (parameter N, npr. 64, 128, itd.).
Shranjevanje kompresiranega zvoka in izvedba dekompresije nad prebranim zvokom.
Predvajanje dekompresiranega zvoka. Alternativno lahko hranite dekompresiran zvok na disk v formatu WAV.
Po izvedbi kompresije izpišite kompresijsko razmerje.