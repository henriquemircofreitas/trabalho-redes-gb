# Relatório técnico dos experimentos

## 1. Objetivo e cadeia de transmissão

O experimento avalia como código de linha, modulação e modelo de canal alteram a taxa de erro de
bits (BER) e a eficiência espectral nominal. Em cada execução, o mesmo texto ASCII de 100.264 bits
passa por codificação de linha, modulação, canal, demodulação e decodificação. A BER é calculada
somente depois da decodificação de linha, sempre em relação aos bits originais da mensagem.

Foram comparados NRZ, Manchester e Manchester diferencial; BPSK, QPSK e 16-QAM; e os canais AWGN
e AWGN com rajadas. Cada ponto representa cinco repetições independentes. Os valores individuais
estão em `results/raw.csv`.

## 2. Comparabilidade e escala de ruído

O eixo é Eb/N0 por bit da mensagem, e não por chip ou por símbolo. A eficiência nominal `η` também
é o número de bits da mensagem por símbolo. Para cada transmissão, o canal mede
`Es = média(|símbolo|²)` e usa `N0 = Es/(η·10^(Eb/N0/10))`. A medição de Es é necessária porque o
texto ASCII não usa todos os rótulos de constelação com a mesma frequência.

No cenário de rajadas, o ruído AWGN de fundo permanece. Um processo Gilbert–Elliott ocupa o estado
ruim em aproximadamente 1% dos símbolos, em rajadas médias de 20 símbolos, acrescentando ruído
equivalente a Eb/N0 de 0 dB. Esse ruído extra não diminui quando o Eb/N0 de fundo aumenta.

## 3. Consistência funcional

Com Eb/N0 infinito, todas as nove combinações de código de linha e modulação recuperaram os
100.264 bits e o texto exatamente, sem violações. O resultado é coberto por nove testes ponta a
ponta. Em AWGN a 20 dB, todas as cinco repetições das nove combinações também registraram zero
erros. Isso separa falhas de implementação dos erros provocados pelo canal.

O programa registra `error_indices`, permitindo mostrar os bits incorretos. Em uma execução de
rajadas com NRZ/16-QAM a 20 dB e semente 0, por exemplo, ocorreram 137 erros; os primeiros índices
foram 9677, 9684, 9692, 9718, 42528, 42536, 62893 e 65563. O agrupamento é compatível com erros em
rajadas, em vez de erros independentes espalhados uniformemente.

## 4. BER × Eb/N0 em AWGN

As curvas AWGN diminuem à medida que Eb/N0 aumenta. Para NRZ, BPSK e QPSK praticamente coincidem
quando comparadas por Eb/N0, como prevê a teoria com mapeamento Gray. A 0 dB, suas BERs médias foram
respectivamente 0,0783 e 0,0780, próximas do valor teórico de aproximadamente 0,07865.

16-QAM oferece mais bits por símbolo, mas exige mais Eb/N0. A 10 dB, NRZ-16-QAM apresentou BER
média de `1,67×10⁻³`, contra `3,99×10⁻⁶` para NRZ-BPSK. Pela interpolação das curvas, BER `10⁻³`
foi atingida aproximadamente em 6,69 dB com NRZ-BPSK, 6,73 dB com NRZ-QPSK e 10,43 dB com
NRZ-16-QAM.

Manchester duplica o número de chips por bit. Como o receptor decide cada chip separadamente, a
energia disponível por decisão cai e aparece uma penalidade próxima de 3 dB. Para BER `10⁻³`,
Manchester-BPSK exigiu 9,69 dB. Manchester diferencial chegou a 10,28 dB: além do custo de dois
chips, uma decisão incorreta pode alterar a relação usada para decodificar o bit seguinte.

## 5. AWGN versus rajadas

Em Eb/N0 baixo, o ruído de fundo domina e as curvas dos dois cenários são próximas. Em Eb/N0 alto,
o AWGN desaparece, mas as curvas de rajadas atingem um piso. A 20 dB, as BERs médias foram:

| Código | BPSK | QPSK | 16-QAM |
|---|---:|---:|---:|
| NRZ | 7,72×10⁻⁴ | 9,24×10⁻⁴ | 1,37×10⁻³ |
| Manchester | 1,63×10⁻³ | 1,43×10⁻³ | 1,68×10⁻³ |
| Manchester diferencial | 2,84×10⁻³ | 2,42×10⁻³ | 3,77×10⁻³ |

Assim, aumentar a potência resolve o AWGN, mas não a degradação adicional independente da SNR de
fundo. Sob rajadas, somente NRZ-BPSK e NRZ-QPSK alcançaram BER `10⁻³` dentro da faixa investigada,
em aproximadamente 8,64 dB e 10,90 dB. NRZ-16-QAM e todos os casos Manchester ficaram limitados
por pisos acima da meta.

## 6. Variabilidade

Cada marcador das figuras mostra a média de cinco BERs. As barras são intervalos de 95% calculados
com `t=2,776` e quatro graus de liberdade. Quando não foi observado erro, o ponto é desenhado como
limite superior pela regra de três: `BER < 3/(5·100264) = 5,98×10⁻⁶`, e não como zero em escala
logarítmica. Os cinco valores individuais permanecem no CSV para auditoria.

A variabilidade relativa aumenta no piso de rajadas porque cada semente produz posições e
comprimentos diferentes. Por exemplo, NRZ-QPSK a 20 dB variou de `6,18×10⁻⁴` a `1,35×10⁻³`.

## 7. Compromisso com eficiência espectral

NRZ maximiza a eficiência: 1, 2 e 4 bit/s/Hz para BPSK, QPSK e 16-QAM. Manchester e Manchester
diferencial reduzem esses valores à metade em troca de transições regulares, sincronismo e detecção
de pares inválidos.

- BPSK é adequada quando robustez e baixa SNR importam mais que largura de banda.
- QPSK duplica a eficiência de BPSK sem penalidade relevante de BER em AWGN coerente ideal.
- 16-QAM alcança 4 bit/s/Hz com NRZ, mas requer SNR maior e sofre piso mais alto nas rajadas.
- Manchester é justificável quando as propriedades de sincronismo da codificação de linha são
  necessárias; neste modelo, não melhora a BER e ainda reduz eficiência.
- Manchester diferencial evita dependência de polaridade absoluta depois de estabelecida a
  referência, mas sua propagação de erros foi desfavorável no canal em rajadas.

Os valores completos aparecem em `results/tradeoff.md` e `results/tradeoff.csv`.

## 8. Constelações e validação teórica

As curvas teóricas sobrepostas ao gráfico NRZ-AWGN concordam com BPSK/QPSK e acompanham a tendência
de 16-QAM. Os diagramas de constelação mostram nuvens largas em 0 dB, agrupamentos distinguíveis em
10 dB e pontos compactos em 20 dB. No canal de rajadas permanecem amostras afastadas mesmo em 20
dB. Alguns pontos ideais aparecem pouco porque o texto ASCII gera rótulos não uniformes; esse efeito
é compensado no dimensionamento do ruído pela energia medida.

## 9. Limitações e conclusão

O modelo assume sincronização perfeita, constelação conhecida, decisão abrupta e pulsos de Nyquist
ideais. Não há estimação de canal, FEC ou retransmissão. Cinco repetições satisfazem o mínimo, mas
mais sementes seriam recomendáveis para estimar pisos muito baixos com maior precisão.

Os resultados confirmam o compromisso central: modulações de ordem superior aumentam a eficiência
espectral, mas exigem mais Eb/N0; códigos Manchester pagam largura de banda e potência por suas
propriedades de transição; e ruído em rajadas cria erros concentrados e um piso que potência de
transmissão adicional não elimina. Portanto, a escolha deve considerar simultaneamente robustez,
largura de banda e natureza do canal, não apenas a BER em AWGN.
