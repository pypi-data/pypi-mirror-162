from datetime import datetime, timedelta
from pprint import pprint
from bson import ObjectId

class Boleta:
    def __init__(self):
        # self.date_created = None
        # self.status = None
        # self.merchant_id = None
        # self.member_id = None
        # self.tries = []
        pass

    def create(self,
               cliente_id,
               merchant_id,
               plan_id,
               source:str,
               status:str='error_not_proccesed',
               charges_detail:dict=dict(),
               opd:datetime=datetime.now(),
               date_created:datetime=datetime.now()
               ):
        try:
            cliente_id = ObjectId(cliente_id)
        except:
            pass
        self.member_id = cliente_id
        self.date_created = date_created
        self.original_payment_date = opd
        self.source = source
        self.tries = list()
        self.status = status
        try:
            merchant_id = ObjectId(merchant_id)
        except:
            pass
        self.merchant_id = merchant_id
        self.charges_detail = charges_detail
        self.period = None
        # Plan
        try:
            plan_id = ObjectId(plan_id)
        except:
            pass
        self.plan_id = plan_id

    def push_to_db(self,db):
        #db = init_mongo()
        if hasattr(self,'_id'):
            result = db.boletas.update_one({'_id': self._id}, {'$set': self.__dict__})
        else:
            result = db.boletas.insert_one(self.__dict__)
        pass

    def import_from_db(self,boleta:dict):
        for key in boleta.keys():
            setattr(self, key, boleta[key])

    def add_try(self,payment_data:dict,card_data:dict=dict()):
        # Complete with card data
        if card_data != dict():
            try:
                payment_data['card_brand'] = card_data['card_brand']
                payment_data['card_id'] = card_data['card_id']
                payment_data['payment_type'] = card_data['payment_type']
            except:
                pass
        # Completa los campos no obligatorios en caso de que no exista
        no_obligatorios = {
            'card_brand':None,
            'card_id':None,
            'payment_type':None
        }
        for key in no_obligatorios.keys():
            if key not in payment_data.keys():
                payment_data[key] = no_obligatorios[key]
        # Genera el nuevo try
        new_try = {
            'try_number':len(self.tries)+1,
            'payment_day':payment_data['payment_day'],
            'payment_type':payment_data['payment_type'],
            'status':payment_data['status'],
            'status_detail':payment_data['status_detail'],
            'card_id':payment_data['card_id'],
            'card_brand':payment_data['card_brand'],
            'payment_id':payment_data['id']
        }
        self.tries.append(new_try)
        pass

    def make_period(self,fecha_de_cobro:datetime,DIAS_DE_ANTICIPO:int=0):
        if 'recurring' in self.source:
            DIAS_DE_ANTICIPO = 7
        fecha_de_cobro += timedelta(days=DIAS_DE_ANTICIPO)
        period = f"{fecha_de_cobro.month}/{fecha_de_cobro.year}"

        self.period = period

    def print(self):
        pprint(self.__dict__)