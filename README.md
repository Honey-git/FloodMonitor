# Flood Monitoring and Alert System

## Visão geral
Este projeto implementa um Sistema de Monitoramento e Alerta de Enchentes em tempo real, projetado para detectar a elevação dos níveis da água e fornecer alertas antecipados em áreas propensas a inundações. O sistema depende principalmente de medições baseadas em sensores e de uma lógica de decisão baseada em regras para uma classificação rápida e confiável dos níveis de enchente.

Além do núcleo baseado em regras, um modelo de aprendizado de máquina (Regressão Logística) é utilizado como uma **camada de validação** para verificar e analisar a consistência dos níveis de risco de inundação gerados. Essa abordagem híbrida aumenta a confiabilidade dos resultados do sistema, mantendo o desempenho em tempo real.

---

## Objetivos
- Monitorar continuamente os níveis da água utilizando sensores
- Classificar os níveis de risco de inundação por meio de regras predefinidas
- Validar as decisões baseadas em regras utilizando um modelo de aprendizado de máquina
- Exibir dados em tempo real e o status dos alertas
- Fornecer uma solução confiável de monitoramento de enchentes com baixa latência

---

## Componentes do Sistema

### Componentes de Hardware
- **Microcontrolador ESP32** – Controlador central para a entrada de dados dos sensores e a execução das regras
- **Sensor Ultrassônico** – Mede a distância até a superfície da água
- **Display LCD** – Exibe o nível da água e o status dos alertas
- **Fonte de Alimentação** – Fornece energia para o funcionamento estável do sistema

---

### Componentes de Software
- Firmware embarcado para ESP32
- Lógica de classificação dos níveis de enchente baseada em regras
- Modelo de aprendizado de máquina para validação e análise
- Lógica de controle do display

---

## Princípio de Funcionamento

1. O sensor ultrassônico mede o nível da água em tempo real.
2. O ESP32 processa os dados do sensor e aplica regras predefinidas de limite.
3. O risco de inundação é classificado em níveis como Seguro, Alerta ou Perigo.
4. O resultado da classificação é exibido no LCD.
5. As leituras do sensor e os resultados gerados pelas regras são enviados ao modelo de aprendizado de máquina.
6. O modelo avalia a consistência da classificação e valida os níveis de agravamento do risco.
7. Eventuais divergências podem ser sinalizadas para análise ou para futuros ajustes do sistema.

---

## Classificação dos Níveis de Enchente (Núcleo Baseado em Regras)

O principal mecanismo de tomada de decisão utiliza regras determinísticas baseadas em limites predefinidos:

- **Nível Seguro** – Nível da água dentro dos limites normais  
- **Nível de Alerta** – Elevação do nível da água que exige atenção  
- **Nível de Perigo** – Nível crítico da água que indica possibilidade de inundação  

Isso garante:
- Resposta rápida
- Comportamento previsível
- Independência de dados de treinamento durante a operação em tempo real

---

## Machine Learning Validation Layer

The ML model is **not used for real-time prediction or control**.  
Instead, it serves as a **secondary validation mechanism**.

### Purpose of ML Integration
- Validate rule-based flood level classifications
- Analyze escalation patterns
- Reduce false alerts through consistency checks
- Support future system optimization

### Key Characteristics
- Operates alongside the rule-based system
- Does not override hardware decisions
- Used for analytical validation rather than actuation
- Can be trained on historical or simulated data

This architecture ensures reliability while enabling data-driven insights.

---

## Testing and Validation

### Hardware Testing
- Individual testing of ESP32, ultrasonic sensor, and LCD
- Verification of sensor accuracy and display updates

### Rule-Based Validation
- Threshold testing using controlled water level variations
- Verification of correct alert triggering

### ML-Based Validation
- Comparison of ML outputs with rule-based classifications
- Evaluation of consistency across different water level scenarios
- Analysis of misclassification or edge cases

---

## Design Considerations
- Real-time responsiveness prioritized
- Rule-based logic retained as authoritative
- ML kept decoupled from hardware control
- Suitable for resource-constrained environments

---

## Limitations
- ML model does not perform real-time prediction
- Accuracy depends on sensor calibration
- Thresholds require location-specific tuning
- No remote alerting or cloud integration in current version

---

## Future Enhancements
- Full IoT-based remote monitoring
- Automated threshold tuning using ML feedback
- SMS / mobile notifications
- Multi-sensor fusion (rainfall, flow rate)
- Cloud-based analytics dashboard

---

## Applications
- Flood-prone urban areas
- Drainage and sewage monitoring
- Bridge and river level monitoring
- Local early warning systems

---

## Conclusion
This project demonstrates a hybrid flood monitoring approach that combines real-time rule-based decision-making with machine learning–based validation. The system prioritizes reliability and responsiveness while enabling intelligent analysis, making it suitable for practical deployment and future smart infrastructure integration.

---

## Author
Developed as an academic project for flood monitoring and early warning applications.