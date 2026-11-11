# Roteiro do vídeo — máximo de 5 minutos

> Substituir os nomes e ensaiar para ficar entre 4min30s e 4min50s.

## 0:00–0:35 — objetivo e arquitetura (Integrante 1)

- Apresentar os dois integrantes.
- Mostrar a cadeia ASCII → código de linha → modulação → canal → receptor → BER.
- Explicar em uma frase que código de linha não é correção de erros.

## 0:35–1:35 — implementação (Integrante 1)

- Mostrar `src/sim/` e citar os três códigos e as três modulações.
- Executar `uv run python experiments/demo.py`.
- Destacar as nove linhas `OK` do teste ideal e os índices dos bits errados nas rajadas.

## 1:35–2:25 — metodologia (Integrante 2)

- Mostrar `results/run_info.json`.
- Citar 100.264 bits, 11 valores de Eb/N0, cinco sementes e 990 execuções.
- Explicar AWGN e o estado ruim de rajadas (1%, média de 20 símbolos).

## 2:25–3:35 — resultados (Integrante 2)

- Mostrar `ber_nrz.png` e apontar a concordância BPSK/QPSK com a teoria.
- Mostrar `comparacao_canais_nrz.png` e o piso de BER sob rajadas.
- Mostrar `constelacoes_16qam.png` em 0, 10 e 20 dB.

## 3:35–4:30 — compromisso e interpretação (ambos)

- Abrir `results/tradeoff.md`.
- Integrante 1: BPSK robusta; QPSK dobra eficiência sem grande penalidade em AWGN.
- Integrante 2: 16-QAM oferece 4 bit/s/Hz com NRZ, mas precisa de maior Eb/N0.
- Explicar o custo de 3 dB e metade da eficiência com Manchester neste receptor.

## 4:30–4:55 — conclusão (ambos)

- AWGN pode ser combatido com potência; a rajada cria piso.
- A escolha depende de potência, largura de banda e natureza do canal.
- Informar que dados brutos, testes e scripts de reprodução estão no GitHub.

## Checklist de gravação

- Os dois integrantes falam e aparecem ou são claramente identificados.
- Terminal com fonte grande; nenhuma chave, notificação ou dado pessoal visível.
- Mostrar execução real, não apenas slides.
- Exportar em MP4 com duração ≤ 5 minutos.
- Publicar no repositório ou em GitHub Release e inserir o link no README.
