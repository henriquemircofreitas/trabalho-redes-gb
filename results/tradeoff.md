# Compromisso entre BER e eficiência espectral

Valores de Eb/N0 foram interpolados em escala logarítmica da BER média.

| Código | Modulação | η (bit/s/Hz) | Eb/N0 p/ BER=10⁻³ AWGN | Eb/N0 p/ BER=10⁻³ rajadas | BER AWGN @10 dB | BER rajadas @10 dB | Indicação |
|---|---:|---:|---:|---:|---:|---:|---|
| NRZ | BPSK | 1.0 | 6.69 dB | 8.64 dB | 3.99e-06 | 0.000852 | canal com pouca SNR; prioriza robustez; máxima eficiência |
| NRZ | QPSK | 2.0 | 6.73 dB | 10.90 dB | 5.98e-06 | 0.00102 | equilíbrio entre robustez e largura de banda; máxima eficiência |
| NRZ | 16-QAM | 4.0 | 10.43 dB | não atingido | 0.00167 | 0.00311 | SNR alta e largura de banda escassa; máxima eficiência |
| Manchester | BPSK | 0.5 | 9.69 dB | não atingido | 0.000718 | 0.00244 | canal com pouca SNR; prioriza robustez; sincronismo e detecção de violações |
| Manchester | QPSK | 1.0 | 9.75 dB | não atingido | 0.00077 | 0.00226 | equilíbrio entre robustez e largura de banda; sincronismo e detecção de violações |
| Manchester | 16-QAM | 2.0 | 12.82 dB | não atingido | 0.0102 | 0.0119 | SNR alta e largura de banda escassa; sincronismo e detecção de violações |
| Manchester diferencial | BPSK | 0.5 | 10.28 dB | não atingido | 0.00161 | 0.00464 | canal com pouca SNR; prioriza robustez; sincronismo e tolerância a inversão de polaridade após referência |
| Manchester diferencial | QPSK | 1.0 | 10.25 dB | não atingido | 0.00151 | 0.00406 | equilíbrio entre robustez e largura de banda; sincronismo e tolerância a inversão de polaridade após referência |
| Manchester diferencial | 16-QAM | 2.0 | 14.09 dB | não atingido | 0.0335 | 0.037 | SNR alta e largura de banda escassa; sincronismo e tolerância a inversão de polaridade após referência |
