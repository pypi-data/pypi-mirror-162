from enum import Enum
from pydantic import BaseModel
import typing as t


__all__ = [
    'COINS',
    'TYPES',
    'STATUS',
    'MarketStats',
]


class _Enum(Enum):
    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    @classmethod
    def dict(cls):
        return {str(e.value): e.value for e in cls}

    @classmethod
    def get(cls, key: str = None):
        if key is None:
            return cls.dict()
        return cls.dict().get(key)


class COINS(_Enum):
    BITCOIN = 'BITCOIN'
    TETHER = 'TETHER'
    ETHEREUM = 'ETHEREUM'
    TOMAN = 'TOMAN'
    RIPPLE = 'RIPPLE'
    BITCOIN_CASH = 'BITCOIN_CASH'
    LITE_COIN = 'LITE_COIN'
    EOS = 'EOS'
    STELLAR = 'STELLAR'
    TRON = 'TRON'
    PAXG = 'PAXG'
    DASH = 'DASH'
    BINANCE_COIN = 'BINANCE_COIN'
    DOGE = 'DOGE'
    CARDANO = 'CARDANO'
    ATOM = 'ATOM'
    MATIC = 'MATIC'
    FANTOM = 'FANTOM'
    POLKADOT = 'POLKADOT'
    SHIBA = 'SHIBA'
    FIL = 'FIL'
    CAKE = 'CAKE'
    CHAIN_LINK = 'CHAIN_LINK'
    UNISWAP = 'UNISWAP'
    THORCHAIN = 'THORCHAIN'
    CHILIZ = 'CHILIZ'
    BIT_TORRENT = 'BIT_TORRENT'
    DECENTRALAND = 'DECENTRALAND'
    AXIE_INFINITY = 'AXIE_INFINITY'
    SANDBOX = 'SANDBOX'
    ENJIN_COIN = 'ENJIN_COIN'
    MY_NEIGHBOR_ALICE = 'MY_NEIGHBOR_ALICE'
    ELROND_EGOLD = 'ELROND_EGOLD'
    AVALANCHE = 'AVALANCHE'
    NEAR_PROTOCOL = 'NEAR_PROTOCOL'
    SOLANA = 'SOLANA'
    TEZOS = 'TEZOS'
    DAI = 'DAI'
    ETHEREUM_CLASSIC = 'ETHEREUM_CLASSIC'
    GALA = 'GALA'
    AAVE = 'AAVE'
    MAKER = 'MAKER'
    ONE_INCH_NETWORK = 'ONE_INCH_NETWORK'
    YFI = 'YFI'
    CELR = 'CELR'
    APE = 'APE'
    POLKASTARTER = 'POLKASTARTER'
    STEPN = 'STEPN'

    @classmethod
    def dict(cls):
        return {
            'BTC': cls.BITCOIN.name,
            'USDT': cls.TETHER.name,
            'ETH': cls.ETHEREUM.name,
            'TMN': cls.TOMAN.name,
            'XRP': cls.RIPPLE.name,
            'BCH': cls.BITCOIN_CASH.name,
            'LTC': cls.LITE_COIN.name,
            'EOS': cls.EOS.name,
            'XLM': cls.STELLAR.name,
            'TRX': cls.TRON.name,
            'PAXG': cls.PAXG.name,
            'DASH': cls.DASH.name,
            'BNB': cls.BINANCE_COIN.name,
            'DOGE': cls.DOGE.name,
            'ADA': cls.CARDANO.name,
            'ATOM': cls.ATOM.name,
            'MATIC': cls.MATIC.name,
            'FTM': cls.FANTOM.name,
            'DOT': cls.POLKADOT.name,
            'SHIB': cls.SHIBA.name,
            'FIL': cls.FIL.name,
            'CAKE': cls.CAKE.name,
            'LINK': cls.CHAIN_LINK.name,
            'UNI': cls.UNISWAP.name,
            'RUNE': cls.THORCHAIN.name,
            'CHZ': cls.CHILIZ.name,
            'BTT': cls.BIT_TORRENT.name,
            'MANA': cls.DECENTRALAND.name,
            'AXS': cls.AXIE_INFINITY.name,
            'SAND': cls.SANDBOX.name,
            'ENJ': cls.ENJIN_COIN.name,
            'ALICE': cls.MY_NEIGHBOR_ALICE.name,
            'EGLD': cls.ELROND_EGOLD.name,
            'AVAX': cls.AVALANCHE.name,
            'NEAR': cls.NEAR_PROTOCOL.name,
            'SOL': cls.SOLANA.name,
            'XTZ': cls.TEZOS.name,
            'DAI': cls.DAI.name,
            'ETC': cls.ETHEREUM_CLASSIC.name,
            'GALA': cls.GALA.name,
            'AAVE': cls.AAVE.name,
            'MAKER': cls.MAKER.name,
            '1INCH': cls.ONE_INCH_NETWORK.name,
            'YFI': cls.YFI.name,
            'CELR': cls.CELR.name,
            'APE': cls.APE.name,
            'POLS': cls.POLKASTARTER.name,
            'GMT': cls.STEPN.name
        }


class TYPES(_Enum):
    QUICK = 'QUICK'
    NORMAL = 'NORMAL'

    @classmethod
    def dict(cls):
        return {
            'LIMIT': cls.NORMAL.value,
            'MARKET': cls.QUICK.value
        }


class STATUS(_Enum):
    CREATED = 'CREATED'
    ORDERING = 'ORDERING'
    ORDERED = 'ORDERED'

    FAILED = 'FAILED'
    FINISHED = 'FINISHED'
    CANCELING = 'CANCELING'
    CANCELED = 'CANCELED'


class MarketStats:
    class Stats(BaseModel):
        sourceCurrency: str
        destinationCurrency: str
        minSourceAmount: float
        maxSourceAmount: float
        minDestinationAmount: float
        sourceAmountDecimalPlace: int
        destinationAmountDecimalPlace: int

    _STATS = {
        'DAI-TETHER': {
            'sourceCurrency': 'DAI',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 10,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': -4
        },
        'DAI-TOMAN': {
            'sourceCurrency': 'DAI',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 10,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': 0
        },
        'BITCOIN-TETHER': {
            'sourceCurrency': 'BITCOIN',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 1e-06,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -5,
            'destinationAmountDecimalPlace': -2
        },
        'ETHEREUM-TETHER': {
            'sourceCurrency': 'ETHEREUM',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 1e-05,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -4,
            'destinationAmountDecimalPlace': -2
        },
        'BITCOIN_CASH-TETHER': {
            'sourceCurrency': 'BITCOIN_CASH',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 1e-05,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -3,
            'destinationAmountDecimalPlace': -2
        },
        'LITE_COIN-TETHER': {
            'sourceCurrency': 'LITE_COIN',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 1e-05,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -3,
            'destinationAmountDecimalPlace': -2
        },
        'DASH-TETHER': {
            'sourceCurrency': 'DASH',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 1e-05,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -3,
            'destinationAmountDecimalPlace': -2
        },
        'RIPPLE-TETHER': {
            'sourceCurrency': 'RIPPLE',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 0.1,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': 0,
            'destinationAmountDecimalPlace': -4
        },
        'STELLAR-TETHER': {
            'sourceCurrency': 'STELLAR',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 0.1,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': 0,
            'destinationAmountDecimalPlace': -4
        },
        'EOS-TETHER': {
            'sourceCurrency': 'EOS',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 0.01,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -1,
            'destinationAmountDecimalPlace': -3
        },
        'TRON-TETHER': {
            'sourceCurrency': 'TRON',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 0.1,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -1,
            'destinationAmountDecimalPlace': -5
        },
        'PAXG-TETHER': {
            'sourceCurrency': 'PAXG',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 1e-06,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -4,
            'destinationAmountDecimalPlace': 0
        },
        'DOGE-TETHER': {
            'sourceCurrency': 'DOGE',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 0.1,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': 0,
            'destinationAmountDecimalPlace': -4
        },
        'CARDANO-TETHER': {
            'sourceCurrency': 'CARDANO',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 0.1,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': 0,
            'destinationAmountDecimalPlace': -4
        },
        'BINANCE_COIN-TETHER': {
            'sourceCurrency': 'BINANCE_COIN',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 0.0001,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -3,
            'destinationAmountDecimalPlace': -1
        },
        'ATOM-TETHER': {
            'sourceCurrency': 'ATOM',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 0.01,
            'maxSourceAmount': 10000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': -2
        },
        'MATIC-TETHER': {
            'sourceCurrency': 'MATIC',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 0.1,
            'maxSourceAmount': 10000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -1,
            'destinationAmountDecimalPlace': -3
        },
        'FANTOM-TETHER': {
            'sourceCurrency': 'FANTOM',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 0.1,
            'maxSourceAmount': 10000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': 0,
            'destinationAmountDecimalPlace': -4
        },
        'POLKADOT-TETHER': {
            'sourceCurrency': 'POLKADOT',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 0.1,
            'maxSourceAmount': 10000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': -2
        },
        'SHIBA-TETHER': {
            'sourceCurrency': 'SHIBA',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 100000,
            'maxSourceAmount': 100000000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': 0,
            'destinationAmountDecimalPlace': -8
        },
        'FIL-TETHER': {
            'sourceCurrency': 'FIL',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 0.1,
            'maxSourceAmount': 10000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': -2
        },
        'CAKE-TETHER': {
            'sourceCurrency': 'CAKE',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 0.1,
            'maxSourceAmount': 10000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': -2
        },
        'CHAIN_LINK-TETHER': {
            'sourceCurrency': 'CHAIN_LINK',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 0.1,
            'maxSourceAmount': 10000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': -2
        },
        'UNISWAP-TETHER': {
            'sourceCurrency': 'UNISWAP',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 0.1,
            'maxSourceAmount': 10000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': -2
        },
        'THORCHAIN-TETHER': {
            'sourceCurrency': 'THORCHAIN',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 5,
            'maxSourceAmount': 10000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -1,
            'destinationAmountDecimalPlace': -2
        },
        'CHILIZ-TETHER': {
            'sourceCurrency': 'CHILIZ',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 0.1,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': 0,
            'destinationAmountDecimalPlace': -4
        },
        'BIT_TORRENT-TETHER': {
            'sourceCurrency': 'BIT_TORRENT',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 13392857.14,
            'maxSourceAmount': 100000000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': 0,
            'destinationAmountDecimalPlace': -8
        },
        'DECENTRALAND-TETHER': {
            'sourceCurrency': 'DECENTRALAND',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 10,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': 0,
            'destinationAmountDecimalPlace': -4
        },
        'AXIE_INFINITY-TETHER': {
            'sourceCurrency': 'AXIE_INFINITY',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 0.62,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': -2
        },
        'SANDBOX-TETHER': {
            'sourceCurrency': 'SANDBOX',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 18,
            'maxSourceAmount': 26000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': 0,
            'destinationAmountDecimalPlace': -4
        },
        'ENJIN_COIN-TETHER': {
            'sourceCurrency': 'ENJIN_COIN',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 10,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -1,
            'destinationAmountDecimalPlace': -3
        },
        'MY_NEIGHBOR_ALICE-TETHER': {
            'sourceCurrency': 'MY_NEIGHBOR_ALICE',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 10,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': -2
        },
        'ELROND_EGOLD-TETHER': {
            'sourceCurrency': 'ELROND_EGOLD',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 0.08,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': -2
        },
        'AVALANCHE-TETHER': {
            'sourceCurrency': 'AVALANCHE',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 0.47,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': -2
        },
        'NEAR_PROTOCOL-TETHER': {
            'sourceCurrency': 'NEAR_PROTOCOL',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 10,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -1,
            'destinationAmountDecimalPlace': -3
        },
        'SOLANA-TETHER': {
            'sourceCurrency': 'SOLANA',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 0.14,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': -2
        },
        'TEZOS-TETHER': {
            'sourceCurrency': 'TEZOS',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 10,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -1,
            'destinationAmountDecimalPlace': -3
        },
        'ETHEREUM_CLASSIC-TETHER': {
            'sourceCurrency': 'ETHEREUM_CLASSIC',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 10,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': -2
        },
        'GALA-TETHER': {
            'sourceCurrency': 'GALA',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 10,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': 0,
            'destinationAmountDecimalPlace': -5
        },
        'AAVE-TETHER': {
            'sourceCurrency': 'AAVE',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 0.12,
            'maxSourceAmount': 500,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -3,
            'destinationAmountDecimalPlace': -1
        },
        'MAKER-TETHER': {
            'sourceCurrency': 'MAKER',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 0.007,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -4,
            'destinationAmountDecimalPlace': 0
        },
        'YFI-TETHER': {
            'sourceCurrency': 'YFI',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 0.002,
            'maxSourceAmount': 0.5,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -5,
            'destinationAmountDecimalPlace': -2
        },
        'CELR-TETHER': {
            'sourceCurrency': 'CELR',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 900,
            'maxSourceAmount': 280000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -1,
            'destinationAmountDecimalPlace': -5
        },
        'APE-TETHER': {
            'sourceCurrency': 'APE',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 1.9,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': -4
        },
        'POLKASTARTER-TETHER': {
            'sourceCurrency': 'POLKASTARTER',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 26,
            'maxSourceAmount': 3500,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -1,
            'destinationAmountDecimalPlace': -3
        },
        'ONE_INCH_NETWORK-TETHER': {
            'sourceCurrency': 'ONE_INCH_NETWORK',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 10,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -1,
            'destinationAmountDecimalPlace': -3
        },
        'STEPN-TETHER': {
            'sourceCurrency': 'STEPN',
            'destinationCurrency': 'TETHER',
            'minSourceAmount': 12.35,
            'maxSourceAmount': 4000,
            'minDestinationAmount': 10,
            'sourceAmountDecimalPlace': -1,
            'destinationAmountDecimalPlace': -5
        },
        'BITCOIN-TOMAN': {
            'sourceCurrency': 'BITCOIN',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 1e-06,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -5,
            'destinationAmountDecimalPlace': 0
        },
        'ETHEREUM-TOMAN': {
            'sourceCurrency': 'ETHEREUM',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 1e-05,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -4,
            'destinationAmountDecimalPlace': 0
        },
        'BITCOIN_CASH-TOMAN': {
            'sourceCurrency': 'BITCOIN_CASH',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 1e-05,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -3,
            'destinationAmountDecimalPlace': 0
        },
        'LITE_COIN-TOMAN': {
            'sourceCurrency': 'LITE_COIN',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 1e-05,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -3,
            'destinationAmountDecimalPlace': 0
        },
        'DASH-TOMAN': {
            'sourceCurrency': 'DASH',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 1e-05,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -3,
            'destinationAmountDecimalPlace': 0
        },
        'RIPPLE-TOMAN': {
            'sourceCurrency': 'RIPPLE',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 0.1,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': 0,
            'destinationAmountDecimalPlace': 0
        },
        'STELLAR-TOMAN': {
            'sourceCurrency': 'STELLAR',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 0.1,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': 0,
            'destinationAmountDecimalPlace': 0
        },
        'EOS-TOMAN': {
            'sourceCurrency': 'EOS',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 0.01,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -1,
            'destinationAmountDecimalPlace': 0
        },
        'TRON-TOMAN': {
            'sourceCurrency': 'TRON',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 0.1,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -1,
            'destinationAmountDecimalPlace': 0
        },
        'PAXG-TOMAN': {
            'sourceCurrency': 'PAXG',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 1e-06,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -4,
            'destinationAmountDecimalPlace': 0
        },
        'DOGE-TOMAN': {
            'sourceCurrency': 'DOGE',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 0.1,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': 0,
            'destinationAmountDecimalPlace': 0
        },
        'CARDANO-TOMAN': {
            'sourceCurrency': 'CARDANO',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 0.1,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': 0,
            'destinationAmountDecimalPlace': 0
        },
        'TETHER-TOMAN': {
            'sourceCurrency': 'TETHER',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 5,
            'maxSourceAmount': 2000,
            'minDestinationAmount': 150000,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': 0
        },
        'BINANCE_COIN-TOMAN': {
            'sourceCurrency': 'BINANCE_COIN',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 0.0001,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -3,
            'destinationAmountDecimalPlace': 0
        },
        'ATOM-TOMAN': {
            'sourceCurrency': 'ATOM',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 0.01,
            'maxSourceAmount': 10000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': 0
        },
        'MATIC-TOMAN': {
            'sourceCurrency': 'MATIC',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 0.1,
            'maxSourceAmount': 10000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -1,
            'destinationAmountDecimalPlace': 0
        },
        'FANTOM-TOMAN': {
            'sourceCurrency': 'FANTOM',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 0.1,
            'maxSourceAmount': 10000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': 0,
            'destinationAmountDecimalPlace': 0
        },
        'POLKADOT-TOMAN': {
            'sourceCurrency': 'POLKADOT',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 0.1,
            'maxSourceAmount': 10000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': 0
        },
        'SHIBA-TOMAN': {
            'sourceCurrency': 'SHIBA',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 100000,
            'maxSourceAmount': 100000000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': 0,
            'destinationAmountDecimalPlace': -3
        },
        'FIL-TOMAN': {
            'sourceCurrency': 'FIL',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 0.1,
            'maxSourceAmount': 10000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': 0
        },
        'CAKE-TOMAN': {
            'sourceCurrency': 'CAKE',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 0.1,
            'maxSourceAmount': 10000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': 0
        },
        'CHAIN_LINK-TOMAN': {
            'sourceCurrency': 'CHAIN_LINK',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 0.1,
            'maxSourceAmount': 10000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': 0
        },
        'UNISWAP-TOMAN': {
            'sourceCurrency': 'UNISWAP',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 0.1,
            'maxSourceAmount': 10000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': 0
        },
        'THORCHAIN-TOMAN': {
            'sourceCurrency': 'THORCHAIN',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 2,
            'maxSourceAmount': 10000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -1,
            'destinationAmountDecimalPlace': 0
        },
        'CHILIZ-TOMAN': {
            'sourceCurrency': 'CHILIZ',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 0.1,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': 0,
            'destinationAmountDecimalPlace': 0
        },
        'BIT_TORRENT-TOMAN': {
            'sourceCurrency': 'BIT_TORRENT',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 6000000,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': 0,
            'destinationAmountDecimalPlace': 0
        },
        'DECENTRALAND-TOMAN': {
            'sourceCurrency': 'DECENTRALAND',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 10,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': 0,
            'destinationAmountDecimalPlace': 0
        },
        'AXIE_INFINITY-TOMAN': {
            'sourceCurrency': 'AXIE_INFINITY',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 0.18,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': 0
        },
        'SANDBOX-TOMAN': {
            'sourceCurrency': 'SANDBOX',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 10,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': 0,
            'destinationAmountDecimalPlace': 0
        },
        'ENJIN_COIN-TOMAN': {
            'sourceCurrency': 'ENJIN_COIN',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 10,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -1,
            'destinationAmountDecimalPlace': 0
        },
        'MY_NEIGHBOR_ALICE-TOMAN': {
            'sourceCurrency': 'MY_NEIGHBOR_ALICE',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 10,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': 0
        },
        'ELROND_EGOLD-TOMAN': {
            'sourceCurrency': 'ELROND_EGOLD',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 0.08,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': 0
        },
        'AVALANCHE-TOMAN': {
            'sourceCurrency': 'AVALANCHE',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 0.16,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': 0
        },
        'NEAR_PROTOCOL-TOMAN': {
            'sourceCurrency': 'NEAR_PROTOCOL',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 10,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -1,
            'destinationAmountDecimalPlace': 0
        },
        'SOLANA-TOMAN': {
            'sourceCurrency': 'SOLANA',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 0.14,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': 0
        },
        'TEZOS-TOMAN': {
            'sourceCurrency': 'TEZOS',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 10,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -1,
            'destinationAmountDecimalPlace': 0
        },
        'ETHEREUM_CLASSIC-TOMAN': {
            'sourceCurrency': 'ETHEREUM_CLASSIC',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 10,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': 0
        },
        'GALA-TOMAN': {
            'sourceCurrency': 'GALA',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 10,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': 0,
            'destinationAmountDecimalPlace': 0
        },
        'AAVE-TOMAN': {
            'sourceCurrency': 'AAVE',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 0.5,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': 0
        },
        'MAKER-TOMAN': {
            'sourceCurrency': 'MAKER',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 0.02,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -4,
            'destinationAmountDecimalPlace': 0
        },
        'YFI-TOMAN': {
            'sourceCurrency': 'YFI',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 0.002,
            'maxSourceAmount': 0.5,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -5,
            'destinationAmountDecimalPlace': 0
        },
        'CELR-TOMAN': {
            'sourceCurrency': 'CELR',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 290,
            'maxSourceAmount': 9000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -1,
            'destinationAmountDecimalPlace': 0
        },
        'APE-TOMAN': {
            'sourceCurrency': 'APE',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 0.6,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': 0
        },
        'POLKASTARTER-TOMAN': {
            'sourceCurrency': 'POLKASTARTER',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 9,
            'maxSourceAmount': 120,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -1,
            'destinationAmountDecimalPlace': 0
        },
        'ONE_INCH_NETWORK-TOMAN': {
            'sourceCurrency': 'ONE_INCH_NETWORK',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 10,
            'maxSourceAmount': 100000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -2,
            'destinationAmountDecimalPlace': 0
        },
        'STEPN-TOMAN': {
            'sourceCurrency': 'STEPN',
            'destinationCurrency': 'TOMAN',
            'minSourceAmount': 15,
            'maxSourceAmount': 2000,
            'minDestinationAmount': 100000,
            'sourceAmountDecimalPlace': -1,
            'destinationAmountDecimalPlace': 0}}

    _STATS_MODEL = {
        'DAI-TETHER': Stats(
            sourceCurrency='DAI',
            destinationCurrency='TETHER',
            minSourceAmount=10,
            maxSourceAmount=100000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=-4
        ),
        'DAI-TOMAN': Stats(
            sourceCurrency='DAI',
            destinationCurrency='TOMAN',
            minSourceAmount=10,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=0
        ),
        'BITCOIN-TETHER': Stats(
            sourceCurrency='BITCOIN',
            destinationCurrency='TETHER',
            minSourceAmount=1e-06,
            maxSourceAmount=100000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-5,
            destinationAmountDecimalPlace=-2
        ),
        'ETHEREUM-TETHER': Stats(
            sourceCurrency='ETHEREUM',
            destinationCurrency='TETHER',
            minSourceAmount=1e-05,
            maxSourceAmount=100000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-4,
            destinationAmountDecimalPlace=-2
        ),
        'BITCOIN_CASH-TETHER': Stats(
            sourceCurrency='BITCOIN_CASH',
            destinationCurrency='TETHER',
            minSourceAmount=1e-05,
            maxSourceAmount=100000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-3,
            destinationAmountDecimalPlace=-2
        ),
        'LITE_COIN-TETHER': Stats(
            sourceCurrency='LITE_COIN',
            destinationCurrency='TETHER',
            minSourceAmount=1e-05,
            maxSourceAmount=100000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-3,
            destinationAmountDecimalPlace=-2
        ),
        'DASH-TETHER': Stats(
            sourceCurrency='DASH',
            destinationCurrency='TETHER',
            minSourceAmount=1e-05,
            maxSourceAmount=100000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-3,
            destinationAmountDecimalPlace=-2
        ),
        'RIPPLE-TETHER': Stats(
            sourceCurrency='RIPPLE',
            destinationCurrency='TETHER',
            minSourceAmount=0.1,
            maxSourceAmount=100000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=0,
            destinationAmountDecimalPlace=-4
        ),
        'STELLAR-TETHER': Stats(
            sourceCurrency='STELLAR',
            destinationCurrency='TETHER',
            minSourceAmount=0.1,
            maxSourceAmount=100000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=0,
            destinationAmountDecimalPlace=-4
        ),
        'EOS-TETHER': Stats(
            sourceCurrency='EOS',
            destinationCurrency='TETHER',
            minSourceAmount=0.01,
            maxSourceAmount=100000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-1,
            destinationAmountDecimalPlace=-3
        ),
        'TRON-TETHER': Stats(
            sourceCurrency='TRON',
            destinationCurrency='TETHER',
            minSourceAmount=0.1,
            maxSourceAmount=100000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-1,
            destinationAmountDecimalPlace=-5
        ),
        'PAXG-TETHER': Stats(
            sourceCurrency='PAXG',
            destinationCurrency='TETHER',
            minSourceAmount=1e-06,
            maxSourceAmount=100000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-4,
            destinationAmountDecimalPlace=0
        ),
        'DOGE-TETHER': Stats(
            sourceCurrency='DOGE',
            destinationCurrency='TETHER',
            minSourceAmount=0.1,
            maxSourceAmount=100000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=0,
            destinationAmountDecimalPlace=-4
        ),
        'CARDANO-TETHER': Stats(
            sourceCurrency='CARDANO',
            destinationCurrency='TETHER',
            minSourceAmount=0.1,
            maxSourceAmount=100000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=0,
            destinationAmountDecimalPlace=-4
        ),
        'BINANCE_COIN-TETHER': Stats(
            sourceCurrency='BINANCE_COIN',
            destinationCurrency='TETHER',
            minSourceAmount=0.0001,
            maxSourceAmount=100000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-3,
            destinationAmountDecimalPlace=-1
        ),
        'ATOM-TETHER': Stats(
            sourceCurrency='ATOM',
            destinationCurrency='TETHER',
            minSourceAmount=0.01,
            maxSourceAmount=10000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=-2
        ),
        'MATIC-TETHER': Stats(
            sourceCurrency='MATIC',
            destinationCurrency='TETHER',
            minSourceAmount=0.1,
            maxSourceAmount=10000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-1,
            destinationAmountDecimalPlace=-3
        ),
        'FANTOM-TETHER': Stats(
            sourceCurrency='FANTOM',
            destinationCurrency='TETHER',
            minSourceAmount=0.1,
            maxSourceAmount=10000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=0,
            destinationAmountDecimalPlace=-4
        ),
        'POLKADOT-TETHER': Stats(
            sourceCurrency='POLKADOT',
            destinationCurrency='TETHER',
            minSourceAmount=0.1,
            maxSourceAmount=10000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=-2
        ),
        'SHIBA-TETHER': Stats(
            sourceCurrency='SHIBA',
            destinationCurrency='TETHER',
            minSourceAmount=100000,
            maxSourceAmount=100000000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=0,
            destinationAmountDecimalPlace=-8
        ),
        'FIL-TETHER': Stats(
            sourceCurrency='FIL',
            destinationCurrency='TETHER',
            minSourceAmount=0.1,
            maxSourceAmount=10000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=-2
        ),
        'CAKE-TETHER': Stats(
            sourceCurrency='CAKE',
            destinationCurrency='TETHER',
            minSourceAmount=0.1,
            maxSourceAmount=10000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=-2
        ),
        'CHAIN_LINK-TETHER': Stats(
            sourceCurrency='CHAIN_LINK',
            destinationCurrency='TETHER',
            minSourceAmount=0.1,
            maxSourceAmount=10000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=-2
        ),
        'UNISWAP-TETHER': Stats(
            sourceCurrency='UNISWAP',
            destinationCurrency='TETHER',
            minSourceAmount=0.1,
            maxSourceAmount=10000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=-2
        ),
        'THORCHAIN-TETHER': Stats(
            sourceCurrency='THORCHAIN',
            destinationCurrency='TETHER',
            minSourceAmount=5,
            maxSourceAmount=10000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-1,
            destinationAmountDecimalPlace=-2
        ),
        'CHILIZ-TETHER': Stats(
            sourceCurrency='CHILIZ',
            destinationCurrency='TETHER',
            minSourceAmount=0.1,
            maxSourceAmount=100000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=0,
            destinationAmountDecimalPlace=-4
        ),
        'BIT_TORRENT-TETHER': Stats(
            sourceCurrency='BIT_TORRENT',
            destinationCurrency='TETHER',
            minSourceAmount=13392857.14,
            maxSourceAmount=100000000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=0,
            destinationAmountDecimalPlace=-8
        ),
        'DECENTRALAND-TETHER': Stats(
            sourceCurrency='DECENTRALAND',
            destinationCurrency='TETHER',
            minSourceAmount=10,
            maxSourceAmount=100000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=0,
            destinationAmountDecimalPlace=-4
        ),
        'AXIE_INFINITY-TETHER': Stats(
            sourceCurrency='AXIE_INFINITY',
            destinationCurrency='TETHER',
            minSourceAmount=0.62,
            maxSourceAmount=100000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=-2
        ),
        'SANDBOX-TETHER': Stats(
            sourceCurrency='SANDBOX',
            destinationCurrency='TETHER',
            minSourceAmount=18,
            maxSourceAmount=26000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=0,
            destinationAmountDecimalPlace=-4
        ),
        'ENJIN_COIN-TETHER': Stats(
            sourceCurrency='ENJIN_COIN',
            destinationCurrency='TETHER',
            minSourceAmount=10,
            maxSourceAmount=100000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-1,
            destinationAmountDecimalPlace=-3
        ),
        'MY_NEIGHBOR_ALICE-TETHER': Stats(
            sourceCurrency='MY_NEIGHBOR_ALICE',
            destinationCurrency='TETHER',
            minSourceAmount=10,
            maxSourceAmount=100000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=-2
        ),
        'ELROND_EGOLD-TETHER': Stats(
            sourceCurrency='ELROND_EGOLD',
            destinationCurrency='TETHER',
            minSourceAmount=0.08,
            maxSourceAmount=100000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=-2
        ),
        'AVALANCHE-TETHER': Stats(
            sourceCurrency='AVALANCHE',
            destinationCurrency='TETHER',
            minSourceAmount=0.47,
            maxSourceAmount=100000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=-2
        ),
        'NEAR_PROTOCOL-TETHER': Stats(
            sourceCurrency='NEAR_PROTOCOL',
            destinationCurrency='TETHER',
            minSourceAmount=10,
            maxSourceAmount=100000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-1,
            destinationAmountDecimalPlace=-3
        ),
        'SOLANA-TETHER': Stats(
            sourceCurrency='SOLANA',
            destinationCurrency='TETHER',
            minSourceAmount=0.14,
            maxSourceAmount=100000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=-2
        ),
        'TEZOS-TETHER': Stats(
            sourceCurrency='TEZOS',
            destinationCurrency='TETHER',
            minSourceAmount=10,
            maxSourceAmount=100000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-1,
            destinationAmountDecimalPlace=-3
        ),
        'ETHEREUM_CLASSIC-TETHER': Stats(
            sourceCurrency='ETHEREUM_CLASSIC',
            destinationCurrency='TETHER',
            minSourceAmount=10,
            maxSourceAmount=100000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=-2
        ),
        'GALA-TETHER': Stats(
            sourceCurrency='GALA',
            destinationCurrency='TETHER',
            minSourceAmount=10,
            maxSourceAmount=100000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=0,
            destinationAmountDecimalPlace=-5
        ),
        'AAVE-TETHER': Stats(
            sourceCurrency='AAVE',
            destinationCurrency='TETHER',
            minSourceAmount=0.12,
            maxSourceAmount=500,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-3,
            destinationAmountDecimalPlace=-1
        ),
        'MAKER-TETHER': Stats(
            sourceCurrency='MAKER',
            destinationCurrency='TETHER',
            minSourceAmount=0.007,
            maxSourceAmount=100000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-4,
            destinationAmountDecimalPlace=0
        ),
        'YFI-TETHER': Stats(
            sourceCurrency='YFI',
            destinationCurrency='TETHER',
            minSourceAmount=0.002,
            maxSourceAmount=0.5,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-5,
            destinationAmountDecimalPlace=-2
        ),
        'CELR-TETHER': Stats(
            sourceCurrency='CELR',
            destinationCurrency='TETHER',
            minSourceAmount=900,
            maxSourceAmount=280000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-1,
            destinationAmountDecimalPlace=-5
        ),
        'APE-TETHER': Stats(
            sourceCurrency='APE',
            destinationCurrency='TETHER',
            minSourceAmount=1.9,
            maxSourceAmount=100000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=-4
        ),
        'POLKASTARTER-TETHER': Stats(
            sourceCurrency='POLKASTARTER',
            destinationCurrency='TETHER',
            minSourceAmount=26,
            maxSourceAmount=3500,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-1,
            destinationAmountDecimalPlace=-3
        ),
        'ONE_INCH_NETWORK-TETHER': Stats(
            sourceCurrency='ONE_INCH_NETWORK',
            destinationCurrency='TETHER',
            minSourceAmount=10,
            maxSourceAmount=100000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-1,
            destinationAmountDecimalPlace=-3
        ),
        'STEPN-TETHER': Stats(
            sourceCurrency='STEPN',
            destinationCurrency='TETHER',
            minSourceAmount=12.35,
            maxSourceAmount=4000,
            minDestinationAmount=10,
            sourceAmountDecimalPlace=-1,
            destinationAmountDecimalPlace=-5
        ),
        'BITCOIN-TOMAN': Stats(
            sourceCurrency='BITCOIN',
            destinationCurrency='TOMAN',
            minSourceAmount=1e-06,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-5,
            destinationAmountDecimalPlace=0
        ),
        'ETHEREUM-TOMAN': Stats(
            sourceCurrency='ETHEREUM',
            destinationCurrency='TOMAN',
            minSourceAmount=1e-05,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-4,
            destinationAmountDecimalPlace=0
        ),
        'BITCOIN_CASH-TOMAN': Stats(
            sourceCurrency='BITCOIN_CASH',
            destinationCurrency='TOMAN',
            minSourceAmount=1e-05,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-3,
            destinationAmountDecimalPlace=0
        ),
        'LITE_COIN-TOMAN': Stats(
            sourceCurrency='LITE_COIN',
            destinationCurrency='TOMAN',
            minSourceAmount=1e-05,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-3,
            destinationAmountDecimalPlace=0
        ),
        'DASH-TOMAN': Stats(
            sourceCurrency='DASH',
            destinationCurrency='TOMAN',
            minSourceAmount=1e-05,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-3,
            destinationAmountDecimalPlace=0
        ),
        'RIPPLE-TOMAN': Stats(
            sourceCurrency='RIPPLE',
            destinationCurrency='TOMAN',
            minSourceAmount=0.1,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=0,
            destinationAmountDecimalPlace=0
        ),
        'STELLAR-TOMAN': Stats(
            sourceCurrency='STELLAR',
            destinationCurrency='TOMAN',
            minSourceAmount=0.1,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=0,
            destinationAmountDecimalPlace=0
        ),
        'EOS-TOMAN': Stats(
            sourceCurrency='EOS',
            destinationCurrency='TOMAN',
            minSourceAmount=0.01,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-1,
            destinationAmountDecimalPlace=0
        ),
        'TRON-TOMAN': Stats(
            sourceCurrency='TRON',
            destinationCurrency='TOMAN',
            minSourceAmount=0.1,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-1,
            destinationAmountDecimalPlace=0
        ),
        'PAXG-TOMAN': Stats(
            sourceCurrency='PAXG',
            destinationCurrency='TOMAN',
            minSourceAmount=1e-06,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-4,
            destinationAmountDecimalPlace=0
        ),
        'DOGE-TOMAN': Stats(
            sourceCurrency='DOGE',
            destinationCurrency='TOMAN',
            minSourceAmount=0.1,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=0,
            destinationAmountDecimalPlace=0
        ),
        'CARDANO-TOMAN': Stats(
            sourceCurrency='CARDANO',
            destinationCurrency='TOMAN',
            minSourceAmount=0.1,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=0,
            destinationAmountDecimalPlace=0
        ),
        'TETHER-TOMAN': Stats(
            sourceCurrency='TETHER',
            destinationCurrency='TOMAN',
            minSourceAmount=5,
            maxSourceAmount=2000,
            minDestinationAmount=150000,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=0
        ),
        'BINANCE_COIN-TOMAN': Stats(
            sourceCurrency='BINANCE_COIN',
            destinationCurrency='TOMAN',
            minSourceAmount=0.0001,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-3,
            destinationAmountDecimalPlace=0
        ),
        'ATOM-TOMAN': Stats(
            sourceCurrency='ATOM',
            destinationCurrency='TOMAN',
            minSourceAmount=0.01,
            maxSourceAmount=10000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=0
        ),
        'MATIC-TOMAN': Stats(
            sourceCurrency='MATIC',
            destinationCurrency='TOMAN',
            minSourceAmount=0.1,
            maxSourceAmount=10000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-1,
            destinationAmountDecimalPlace=0
        ),
        'FANTOM-TOMAN': Stats(
            sourceCurrency='FANTOM',
            destinationCurrency='TOMAN',
            minSourceAmount=0.1,
            maxSourceAmount=10000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=0,
            destinationAmountDecimalPlace=0
        ),
        'POLKADOT-TOMAN': Stats(
            sourceCurrency='POLKADOT',
            destinationCurrency='TOMAN',
            minSourceAmount=0.1,
            maxSourceAmount=10000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=0
        ),
        'SHIBA-TOMAN': Stats(
            sourceCurrency='SHIBA',
            destinationCurrency='TOMAN',
            minSourceAmount=100000,
            maxSourceAmount=100000000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=0,
            destinationAmountDecimalPlace=-3
        ),
        'FIL-TOMAN': Stats(
            sourceCurrency='FIL',
            destinationCurrency='TOMAN',
            minSourceAmount=0.1,
            maxSourceAmount=10000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=0
        ),
        'CAKE-TOMAN': Stats(
            sourceCurrency='CAKE',
            destinationCurrency='TOMAN',
            minSourceAmount=0.1,
            maxSourceAmount=10000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=0
        ),
        'CHAIN_LINK-TOMAN': Stats(
            sourceCurrency='CHAIN_LINK',
            destinationCurrency='TOMAN',
            minSourceAmount=0.1,
            maxSourceAmount=10000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=0
        ),
        'UNISWAP-TOMAN': Stats(
            sourceCurrency='UNISWAP',
            destinationCurrency='TOMAN',
            minSourceAmount=0.1,
            maxSourceAmount=10000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=0
        ),
        'THORCHAIN-TOMAN': Stats(
            sourceCurrency='THORCHAIN',
            destinationCurrency='TOMAN',
            minSourceAmount=2,
            maxSourceAmount=10000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-1,
            destinationAmountDecimalPlace=0
        ),
        'CHILIZ-TOMAN': Stats(
            sourceCurrency='CHILIZ',
            destinationCurrency='TOMAN',
            minSourceAmount=0.1,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=0,
            destinationAmountDecimalPlace=0
        ),
        'BIT_TORRENT-TOMAN': Stats(
            sourceCurrency='BIT_TORRENT',
            destinationCurrency='TOMAN',
            minSourceAmount=6000000,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=0,
            destinationAmountDecimalPlace=0
        ),
        'DECENTRALAND-TOMAN': Stats(
            sourceCurrency='DECENTRALAND',
            destinationCurrency='TOMAN',
            minSourceAmount=10,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=0,
            destinationAmountDecimalPlace=0
        ),
        'AXIE_INFINITY-TOMAN': Stats(
            sourceCurrency='AXIE_INFINITY',
            destinationCurrency='TOMAN',
            minSourceAmount=0.18,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=0
        ),
        'SANDBOX-TOMAN': Stats(
            sourceCurrency='SANDBOX',
            destinationCurrency='TOMAN',
            minSourceAmount=10,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=0,
            destinationAmountDecimalPlace=0
        ),
        'ENJIN_COIN-TOMAN': Stats(
            sourceCurrency='ENJIN_COIN',
            destinationCurrency='TOMAN',
            minSourceAmount=10,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-1,
            destinationAmountDecimalPlace=0
        ),
        'MY_NEIGHBOR_ALICE-TOMAN': Stats(
            sourceCurrency='MY_NEIGHBOR_ALICE',
            destinationCurrency='TOMAN',
            minSourceAmount=10,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=0
        ),
        'ELROND_EGOLD-TOMAN': Stats(
            sourceCurrency='ELROND_EGOLD',
            destinationCurrency='TOMAN',
            minSourceAmount=0.08,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=0
        ),
        'AVALANCHE-TOMAN': Stats(
            sourceCurrency='AVALANCHE',
            destinationCurrency='TOMAN',
            minSourceAmount=0.16,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=0
        ),
        'NEAR_PROTOCOL-TOMAN': Stats(
            sourceCurrency='NEAR_PROTOCOL',
            destinationCurrency='TOMAN',
            minSourceAmount=10,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-1,
            destinationAmountDecimalPlace=0
        ),
        'SOLANA-TOMAN': Stats(
            sourceCurrency='SOLANA',
            destinationCurrency='TOMAN',
            minSourceAmount=0.14,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=0
        ),
        'TEZOS-TOMAN': Stats(
            sourceCurrency='TEZOS',
            destinationCurrency='TOMAN',
            minSourceAmount=10,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-1,
            destinationAmountDecimalPlace=0
        ),
        'ETHEREUM_CLASSIC-TOMAN': Stats(
            sourceCurrency='ETHEREUM_CLASSIC',
            destinationCurrency='TOMAN',
            minSourceAmount=10,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=0
        ),
        'GALA-TOMAN': Stats(
            sourceCurrency='GALA',
            destinationCurrency='TOMAN',
            minSourceAmount=10,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=0,
            destinationAmountDecimalPlace=0
        ),
        'AAVE-TOMAN': Stats(
            sourceCurrency='AAVE',
            destinationCurrency='TOMAN',
            minSourceAmount=0.5,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=0
        ),
        'MAKER-TOMAN': Stats(
            sourceCurrency='MAKER',
            destinationCurrency='TOMAN',
            minSourceAmount=0.02,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-4,
            destinationAmountDecimalPlace=0
        ),
        'YFI-TOMAN': Stats(
            sourceCurrency='YFI',
            destinationCurrency='TOMAN',
            minSourceAmount=0.002,
            maxSourceAmount=0.5,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-5,
            destinationAmountDecimalPlace=0
        ),
        'CELR-TOMAN': Stats(
            sourceCurrency='CELR',
            destinationCurrency='TOMAN',
            minSourceAmount=290,
            maxSourceAmount=9000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-1,
            destinationAmountDecimalPlace=0
        ),
        'APE-TOMAN': Stats(
            sourceCurrency='APE',
            destinationCurrency='TOMAN',
            minSourceAmount=0.6,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=0
        ),
        'POLKASTARTER-TOMAN': Stats(
            sourceCurrency='POLKASTARTER',
            destinationCurrency='TOMAN',
            minSourceAmount=9,
            maxSourceAmount=120,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-1,
            destinationAmountDecimalPlace=0
        ),
        'ONE_INCH_NETWORK-TOMAN': Stats(
            sourceCurrency='ONE_INCH_NETWORK',
            destinationCurrency='TOMAN',
            minSourceAmount=10,
            maxSourceAmount=100000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-2,
            destinationAmountDecimalPlace=0
        ),
        'STEPN-TOMAN': Stats(
            sourceCurrency='STEPN',
            destinationCurrency='TOMAN',
            minSourceAmount=15,
            maxSourceAmount=2000,
            minDestinationAmount=100000,
            sourceAmountDecimalPlace=-1,
            destinationAmountDecimalPlace=0)}

    @classmethod
    def get(cls, item: str) -> t.Dict[str, t.Union[str, float, int]]:
        return cls._STATS[item]

    @classmethod
    def load(cls, item: str) -> Stats:
        return cls.Stats(**cls.get(item))

    @classmethod
    def find(cls, source: str, destination: str) -> t.Dict[str, t.Union[str, float, int]]:
        return cls._STATS[f'{source}-{destination}']

    @classmethod
    def load_find(cls, source: str, destination: str) -> Stats:
        return cls.Stats(**cls.find(source, destination))
