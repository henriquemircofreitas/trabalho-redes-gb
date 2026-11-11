# Roteiro da apresentação oral — 10 minutos

| Tempo | Slide | Conteúdo | Responsável |
|---:|---|---|---|
| 0:00–0:45 | 1 | Problema, objetivo e integrantes | Ambos |
| 0:45–1:40 | 2 | Cadeia ponta a ponta e arquitetura | Integrante 1 |
| 1:40–2:35 | 3 | Código de linha × correção de erros | Integrante 1 |
| 2:35–3:30 | 4 | BPSK, QPSK, 16-QAM, Gray e eficiência | Integrante 1 |
| 3:30–4:25 | 5 | AWGN, Eb/N0 justo e modelo de rajadas | Integrante 2 |
| 4:25–5:10 | 6 | Plano: 100.264 bits, 11 SNRs, 5 sementes | Integrante 2 |
| 5:10–6:20 | 7 | BER em AWGN, teoria e intervalos | Integrante 2 |
| 6:20–7:20 | 8 | AWGN × rajadas e recuperação da mensagem | Integrante 2 |
| 7:20–8:20 | 9 | Tabela BER × eficiência espectral | Ambos |
| 8:20–9:10 | 10 | Consistência, constelações e limitações | Integrante 1 |
| 9:10–10:00 | 11 | Conclusões e recomendação por cenário | Ambos |

## Perguntas prováveis

**Por que BPSK e QPSK têm BER semelhante?**  
Em detecção coerente ideal e comparação por Eb/N0, cada bit vê a mesma distância efetiva; QPSK
transporta dois bits ortogonais por símbolo.

**Por que Manchester ficou cerca de 3 dB pior?**  
Cada bit vira dois chips e a energia por bit é dividida. O receptor decide os chips separadamente,
sem combinação suave.

**Por que a curva de rajadas não vai a zero?**  
O estado ruim acrescenta ruído absoluto independente do AWGN de fundo; aumentar Eb/N0 reduz apenas
o fundo.

**Por que cinco repetições?**  
É o mínimo solicitado. Mantivemos os valores individuais e mostramos IC de 95%; reconhecemos que
mais sementes melhorariam a estimativa de BER muito baixa.

**NRZ é realmente código de linha?**  
Sim, é uma codificação de linha binária de referência. O projeto também implementa duas técnicas
com transições explícitas, Manchester e Manchester diferencial, portanto não depende apenas do NRZ
para cumprir o mínimo.
