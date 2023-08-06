from logging import getLogger
import pandas as pd

PRESSAO_ESTATICA = 3000
PRESSAO_DE_BOLHA = 10
PRESSAO_FUNDO_POCO_1 = 1900
VAZAO = 500
NUMERO_PONTOS = 301


def calculo_vazao_linear(
    pressao_estatica,
    pressao_fundo_poco_1,
    vazao,
    delta_pressao,
):
    ip = vazao / (pressao_estatica - pressao_fundo_poco_1)
    pressoes = []
    vazoes = []
    pressao_fundo_poco = pressao_estatica
    while pressao_fundo_poco >= 0:
        q = ip * (pressao_estatica - pressao_fundo_poco)

        pressoes.append(pressao_fundo_poco)
        vazoes.append(q)
        pressao_fundo_poco -= delta_pressao

    return pd.DataFrame(data=dict(pressoes=pressoes, vazoes=vazoes))


def calculo_vazao_vogel(
    pressao_estatica,
    pressao_fundo_poco_1,
    vazao,
    delta_pressao,
):
    q_max = vazao / (
        1
        - (0.2 * (pressao_fundo_poco_1 / pressao_estatica))
        - (0.8 * (pressao_fundo_poco_1 / pressao_estatica) ** 2)
    )

    pressoes = []
    vazoes = []
    pressao_fundo_poco = pressao_estatica
    while pressao_fundo_poco >= 0:
        q = q_max * (
            1
            - (0.2 * (pressao_fundo_poco / pressao_estatica))
            - (0.8 * (pressao_fundo_poco / pressao_estatica) ** 2)
        )

        pressoes.append(pressao_fundo_poco)
        vazoes.append(q)
        pressao_fundo_poco -= delta_pressao

    return pd.DataFrame(data=dict(pressoes, vazoes))


def calculo_vazao_vogel_combinada(
    pressao_estatica,
    pressao_de_bolha,
    pressao_fundo_poco_1,
    vazao,
    delta_pressao,
):

    ip = vazao / (pressao_estatica - pressao_fundo_poco_1)
    qx = vazao / (
        1.8 * (pressao_estatica / pressao_de_bolha)
        - (0.8)
        - 0.2 * (pressao_fundo_poco_1 / pressao_de_bolha)
        - 0.8 * ((pressao_fundo_poco_1 / pressao_de_bolha) ** 2)
    )

    pressoes = []
    vazoes = []
    pressao_fundo_poco = pressao_estatica

    while pressao_fundo_poco >= 0:
        if pressao_fundo_poco > pressao_de_bolha:
            q = ip * (pressao_estatica - pressao_fundo_poco)
        else:
            q = qx * (
                1.8 * (pressao_estatica / pressao_de_bolha)
                - (0.8)
                - (0.2 * (pressao_fundo_poco / pressao_de_bolha))
                - (0.8 * (pressao_fundo_poco / pressao_de_bolha) ** 2)
            )

        pressoes.append(pressao_fundo_poco)
        vazoes.append(q)
        pressao_fundo_poco -= delta_pressao

    return pd.DataFrame(data=dict(pressoes=pressoes, vazoes=vazoes))


def main(
    pressao_estatica,
    pressao_de_bolha,
    pressao_fundo_poco_1,
    vazao,
    numero_pontos=NUMERO_PONTOS,
):
    delta_pressao = pressao_estatica / numero_pontos

    vogel = pressao_estatica < pressao_de_bolha
    vogel_combinada = pressao_de_bolha > delta_pressao
    linear = (pressao_estatica > pressao_de_bolha) and (
        pressao_de_bolha <= delta_pressao
    )

    if linear:
        return calculo_vazao_linear(
            pressao_estatica,
            pressao_fundo_poco_1,
            vazao,
            delta_pressao,
        )
    if vogel:
        return calculo_vazao_vogel(
            pressao_estatica,
            pressao_fundo_poco_1,
            vazao,
            delta_pressao,
        )
    if vogel_combinada:
        return calculo_vazao_vogel_combinada(
            pressao_estatica,
            pressao_de_bolha,
            pressao_fundo_poco_1,
            vazao,
            delta_pressao,
        )
