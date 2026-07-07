"""Enums de dominio: tipos de matriz, plan, KPI, perspectiva, sentido, frecuencia."""
from enum import Enum


class TipoMatriz(str, Enum):
    holmes = "holmes"
    foda_cuali = "foda_cuali"
    foda_cuanti = "foda_cuanti"
    efi = "efi"
    efe = "efe"
    cadena_valor = "cadena_valor"
    aoor = "aoor"
    aprovechabilidad = "aprovechabilidad"
    cinco_fuerzas = "cinco_fuerzas"
    mpc = "mpc"
    ansoff = "ansoff"
    pestel = "pestel"
    peyea = "peyea"
    madi = "madi"
    made = "made"


class TipoPlan(str, Enum):
    financiero = "financiero"
    marketing = "marketing"
    operaciones = "operaciones"
    mejoras = "mejoras"
    tecnologico = "tecnologico"
    compras = "compras"
    control = "control"


class TipoPerspectiva(str, Enum):
    financiera = "financiera"
    clientes = "clientes"
    procesos = "procesos"
    aprendizaje = "aprendizaje"


class Sentido(str, Enum):
    directo = "directo"
    inverso = "inverso"


class TipoPeriodo(str, Enum):
    mensual = "mensual"
    trimestral = "trimestral"
    semestral = "semestral"
    anual = "anual"
    ciclo_cosecha = "ciclo_cosecha"
