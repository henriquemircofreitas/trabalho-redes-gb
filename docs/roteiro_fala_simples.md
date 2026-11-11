# Roteiro de fala simples — 10 minutos

Este roteiro acompanha `apresentacao_redes_gb.pptx`. A divisão é exatamente metade para cada
integrante: **Bernardo fala por 5 minutos e Henrique fala por 5 minutos**.

Não é necessário decorar palavra por palavra. O ideal é entender a ideia de cada trecho, ensaiar
duas ou três vezes e falar olhando para a turma. Os termos técnicos são explicados antes de serem
usados.

## Divisão do tempo

| Slide | Assunto | Quem fala | Tempo |
|---:|---|---|---:|
| 1 | Abertura | Bernardo | 30 s |
| 2 | Caminho da mensagem | Bernardo | 55 s |
| 3 | Códigos de linha | Bernardo | 1 min 05 s |
| 4 | Modulações | Bernardo | 1 min |
| 5 | Canais | Bernardo | 1 min |
| 6 | Metodologia | Henrique | 45 s |
| 7 | Resultado em AWGN | Henrique | 1 min 05 s |
| 8 | Resultado com rajadas | Henrique | 1 min 05 s |
| 9 | Eficiência espectral | Henrique | 55 s |
| 10 | Validação e constelações | Henrique | 50 s |
| 11 | Conclusão | Bernardo 30 s + Henrique 20 s | 50 s |

**Total de Bernardo: 5 minutos. Total de Henrique: 5 minutos.**

---

## Slide 1 — Abertura

**Bernardo — 30 segundos**

> Boa noite. Nós somos Bernardo e Henrique, e o nosso trabalho simula uma transmissão digital do
> começo ao fim. Em outras palavras, nós pegamos um texto normal, transformamos esse texto em bits,
> enviamos esses bits por um canal com ruído e tentamos recuperar a mensagem no outro lado. O nosso
> objetivo foi descobrir como diferentes formas de transmissão mudam a quantidade de erros e o uso
> da largura de banda.

**Transição:** “Primeiro eu vou mostrar o caminho que a mensagem percorre.”

## Slide 2 — Do texto ao bit recuperado

**Bernardo — 55 segundos**

> A mensagem começa como um texto em ASCII. ASCII é uma tabela que representa cada letra, número
> ou símbolo usando oito bits. A nossa mensagem possui 12.533 caracteres, o que resulta em 100.264
> bits. Depois aplicamos um código de linha, que organiza como esses bits aparecem no sinal. Em
> seguida, vários bits são agrupados em símbolos pela modulação. O canal adiciona ruído, como se
> fosse um chiado atrapalhando a comunicação. No receptor fazemos o processo contrário até voltar ao
> texto. No final comparamos cada bit recebido com o original. A BER é justamente a proporção de bits
> que chegaram errados.

**Se quiser dar um exemplo:** BER de `0,001` significa aproximadamente um bit errado a cada mil.

## Slide 3 — Código de linha não é correção de erros

**Bernardo — 1 minuto e 5 segundos**

> Aqui aparecem os três códigos de linha que implementamos. No NRZ, cada bit é representado
> diretamente por um nível. No Manchester, cada bit vira dois pequenos intervalos, que chamamos de
> chips, e sempre existe uma mudança no meio. Isso ajuda o receptor a acompanhar o ritmo da
> transmissão. O Manchester diferencial também usa transições, mas interpreta a informação pela
> mudança em relação ao nível anterior.
>
> É importante não confundir código de linha com correção de erros. O código de linha muda o formato
> do sinal. No Manchester, se recebermos `00` ou `11`, sabemos que aconteceu algo errado, porque esses
> pares não são válidos. Porém não sabemos com certeza qual era o bit original. Então conseguimos
> detectar algumas violações, mas não corrigir o erro. Um código corretor teria uma redundância
> própria para descobrir e recuperar a informação perdida.

## Slide 4 — BPSK, QPSK e 16-QAM

**Bernardo — 1 minuto**

> Modulação é a forma de transformar bits em símbolos que podem ser transmitidos. Podemos imaginar
> cada ponto do desenho como uma opção do alfabeto usado pelo transmissor. A BPSK tem apenas dois
> pontos e transporta um bit por símbolo. A QPSK tem quatro pontos e transporta dois bits. A 16-QAM
> tem dezesseis pontos e transporta quatro bits por símbolo.
>
> Colocar mais bits em cada símbolo aumenta a eficiência, porque enviamos mais informação no mesmo
> espaço. O problema é que os pontos ficam mais próximos. Com ruído, o receptor pode confundir um
> ponto com o vizinho. Usamos mapeamento Gray, no qual pontos vizinhos diferem em apenas um bit, para
> diminuir o prejuízo quando essa confusão acontece.

## Slide 5 — AWGN e ruído em rajadas

**Bernardo — 1 minuto**

> Testamos dois tipos de canal. O primeiro é o AWGN, que representa um ruído aleatório parecido com
> um chiado contínuo. Quando aumentamos Eb sobre N0, melhoramos a relação entre a energia do bit e o
> ruído. Em termos simples, o sinal fica mais fácil de distinguir.
>
> O segundo canal mantém esse chiado e acrescenta rajadas. É como uma interferência forte que aparece
> por alguns instantes e depois desaparece. O canal fica no estado ruim em cerca de um por cento dos
> símbolos, e cada rajada dura em média vinte símbolos. O ruído da rajada não diminui quando aumentamos
> a qualidade do sinal de fundo. Por isso esperávamos que esse canal continuasse apresentando erros
> mesmo em valores altos de Eb sobre N0.

**Passagem de fala:** “Agora o Henrique vai explicar como organizamos os experimentos e o que os
resultados mostraram.”

## Slide 6 — Como o experimento foi feito

**Henrique — 45 segundos**

> Para que a comparação fosse justa, todas as combinações usaram os mesmos parâmetros. Cada
> transmissão enviou 100.264 bits. Testamos onze valores de Eb sobre N0, começando em zero e indo até
> vinte decibéis. Cada ponto foi repetido cinco vezes com sementes aleatórias diferentes. Com três
> códigos de linha, três modulações, dois canais, onze valores e cinco repetições, chegamos a 990
> execuções completas. No total foram mais de 99 milhões de bits. Também salvamos cada resultado em
> CSV, junto com as configurações e os scripts necessários para repetir tudo.

## Slide 7 — Resultado no canal AWGN

**Henrique — 1 minuto e 5 segundos**

> Este gráfico mostra a BER no eixo vertical e Eb sobre N0 no eixo horizontal. Quanto mais baixa a
> curva, menos erros tivemos. No lado esquerdo está o AWGN. BPSK e QPSK ficaram praticamente juntas,
> o que era esperado pela teoria quando a comparação é feita por energia de cada bit. As linhas
> tracejadas representam os valores teóricos e ficaram próximas da simulação, servindo como uma
> validação independente do programa.
>
> Para chegar a uma BER de um erro a cada mil bits, a BPSK com NRZ precisou de aproximadamente 6,69
> decibéis. A 16-QAM precisou de 10,43 decibéis. Isso confirma que a 16-QAM envia mais informação,
> mas exige um sinal de melhor qualidade. As pequenas barras mostram a variação entre as cinco
> repetições.

## Slide 8 — O efeito das rajadas

**Henrique — 1 minuto e 5 segundos**

> Neste gráfico comparamos diretamente o AWGN com o canal de rajadas. No AWGN, as curvas continuam
> caindo quando aumentamos Eb sobre N0, porque o ruído de fundo fica menos importante. No canal de
> rajadas, as curvas param de cair e formam um piso. Isso acontece porque a interferência forte das
> rajadas continua existindo, mesmo quando o restante do canal está bom.
>
> Em vinte decibéis, por exemplo, ainda medimos uma BER média de aproximadamente `7,72 vezes 10
> elevado a menos 4` na BPSK, `9,24 vezes 10 elevado a menos 4` na QPSK e `1,37 vezes 10 elevado a
> menos 3` na 16-QAM, usando NRZ. A principal conclusão é que aumentar somente a potência ajuda no
> AWGN, mas não elimina uma degradação que acontece em rajadas.

## Slide 9 — BER versus eficiência espectral

**Henrique — 55 segundos**

> Eficiência espectral indica quanta informação conseguimos enviar usando a mesma largura de banda.
> É parecido com comparar quantas pessoas cabem em um veículo: colocar mais pessoas aproveita melhor
> o espaço, mas pode exigir um sistema mais cuidadoso.
>
> Com NRZ, a BPSK entrega um bit por segundo por hertz, a QPSK entrega dois e a 16-QAM entrega quatro.
> A QPSK foi o melhor equilíbrio no nosso cenário: dobrou a eficiência da BPSK e praticamente não
> precisou de Eb sobre N0 adicional no AWGN ideal. A 16-QAM alcançou a maior eficiência, mas exigiu
> mais qualidade de sinal. Manchester reduz a eficiência pela metade porque utiliza dois chips para
> representar cada bit.

## Slide 10 — Teste de consistência e constelações

**Henrique — 50 segundos**

> Antes de confiar nos gráficos, verificamos se o sistema funcionava corretamente. Em um canal sem
> ruído, as nove combinações de código de linha e modulação recuperaram exatamente todos os 100.264
> bits. Em AWGN a vinte decibéis também tivemos zero erros nas cinco repetições.
>
> Os desenhos à esquerda mostram a constelação da 16-QAM. Em zero decibéis, os pontos recebidos ficam
> espalhados e se misturam. Em dez decibéis, os grupos começam a ficar claros. Em vinte decibéis,
> eles ficam concentrados perto dos pontos ideais. No canal de rajadas ainda aparecem alguns pontos
> afastados. Além disso, o repositório possui 26 testes automáticos executados pelo GitHub.

## Slide 11 — Conclusões

**Bernardo — 30 segundos**

> Como conclusão, vimos três ideias principais. Primeiro, em AWGN, aumentar a qualidade do sinal
> reduz os erros, e os resultados acompanharam a teoria. Segundo, as rajadas criam um piso de BER,
> então mais potência sozinha não resolve tudo. Terceiro, não existe uma modulação melhor em todos os
> casos: a escolha depende da largura de banda disponível, da qualidade do canal e da quantidade de
> erros aceitável.

**Henrique — 20 segundos**

> No nosso experimento, QPSK com NRZ apresentou o melhor equilíbrio geral. BPSK foi a opção mais
> robusta e 16-QAM foi a mais eficiente quando havia sinal suficiente. Todo o código, os dados brutos,
> os gráficos e os testes estão disponíveis no GitHub. Obrigado. Estamos à disposição para perguntas.

---

## Cola rápida dos termos técnicos

- **Bit:** menor unidade de informação, representada por zero ou um.
- **Chip:** parte do sinal criada pelo código de linha. Um bit pode virar um ou dois chips.
- **Símbolo:** ponto transmitido pela modulação; pode carregar um ou vários bits.
- **BER:** número de bits errados dividido pelo total de bits transmitidos.
- **Eb/N0:** comparação entre a energia de cada bit e o nível de ruído. Valor maior normalmente
  significa recepção mais fácil.
- **Eficiência espectral:** quantidade de bits transmitidos por segundo em cada hertz disponível.
- **AWGN:** modelo de ruído aleatório contínuo, parecido com chiado.
- **Rajada:** período curto em que o canal fica muito mais ruidoso.
- **Mapeamento Gray:** organização em que pontos vizinhos diferem em apenas um bit.
- **Intervalo de confiança:** faixa que mostra quanto o resultado variou entre as repetições.

## Perguntas que o professor pode fazer

### Por que BPSK e QPSK tiveram BER parecida?

Porque a comparação foi feita usando a mesma energia por bit. Em um receptor ideal, a QPSK equivale
a duas transmissões BPSK independentes, uma em cada eixo da constelação.

### Por que Manchester ficou aproximadamente 3 dB pior?

Porque cada bit foi dividido em dois chips e o receptor decidiu cada chip separadamente. Assim,
cada decisão recebeu aproximadamente metade da energia.

### Por que usar 100.264 bits?

O enunciado exige pelo menos 100 mil bits por combinação. O texto escolhido possui 12.533
caracteres ASCII, com oito bits por caractere, resultando em 100.264 bits.

### Por que fazer cinco repetições?

É o mínimo solicitado no trabalho. As repetições permitem mostrar que o resultado não depende de
uma única sequência de ruído e possibilitam calcular a variabilidade.

### Por que a curva de rajadas não chegou a zero?

Porque o ruído extra do estado ruim tem nível fixo e não diminui junto com o AWGN de fundo. Isso
produz um piso de erros.

### Qual combinação vocês escolheriam?

Depende do cenário. BPSK para máxima robustez, QPSK/NRZ para equilíbrio geral e 16-QAM/NRZ quando a
largura de banda for limitada e houver boa relação sinal-ruído.

### Código de linha é código de canal?

Não. Código de linha organiza a representação elétrica dos bits. Código de canal ou FEC acrescenta
redundância especificamente para detectar e corrigir erros.

## Dicas para apresentar

1. Falem um pouco mais devagar nos slides 7 e 8, que concentram os resultados.
2. Não leiam os números dígito por dígito; expliquem o que eles significam.
3. Quando disserem “curva mais baixa”, apontem para a parte inferior do gráfico.
4. Na troca do slide 5 para o 6, Bernardo chama Henrique pelo nome. Isso deixa a divisão clara.
5. No slide final, os dois devem olhar para a turma, não para a tela.
6. Se o tempo estiver acabando, resumam o slide 10; não cortem a conclusão.
