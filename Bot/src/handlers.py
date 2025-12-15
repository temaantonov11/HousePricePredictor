from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import src.keyboards as keyboard
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from src.predict import predict_apartment_price

class House(StatesGroup):
    area = State()
    living_area = State()
    kitchen_area = State()
    number_of_rooms = State()
    minutes_to_metro = State()
    number_of_floors = State()
    floor = State()
    apartment_type = State()
    metro_station = State()
    renovation = State()

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply('Привет!\n Чтобы посчитать стоимость квартиры тебе нужно нажать на кнопку ниже и ввести ее параметры', reply_markup=keyboard.main)

@router.message(F.text == 'Посчитать стоимость квартиры')
async def request_area(message: Message, state: FSMContext):
    await state.set_state(House.area)
    await message.answer('Введите площадь квартиры')

@router.message(House.area)
async def handle_area_req_living_area(message: Message, state: FSMContext):
    await state.update_data(area=message.text)
    await state.set_state(House.living_area)
    await message.answer('Введите суммарную площадь комнат')

@router.message(House.living_area)
async def handle_living_area_req_kitchen_area(message: Message, state: FSMContext):
    await state.update_data(living_area=message.text)
    await state.set_state(House.kitchen_area)
    await message.answer('Введите площадь кухни')

@router.message(House.kitchen_area)
async def handle_kitchen_area_req_number_of_rooms(message: Message, state: FSMContext):
    await state.update_data(kitchen_area=message.text)
    await state.set_state(House.number_of_rooms)
    await message.answer('Введите количество комнат')

@router.message(House.number_of_rooms)
async def handle_number_of_rooms_req_minutes_to_metro(message: Message, state: FSMContext):
    await state.update_data(number_of_rooms=message.text)
    await state.set_state(House.minutes_to_metro)
    await message.answer('Введите количество минут до метро')

@router.message(House.minutes_to_metro)
async def handle_minutes_to_metro_req_number_of_floors(message: Message, state: FSMContext):
    await state.update_data(minutes_to_metro=message.text)
    await state.set_state(House.number_of_floors)
    await message.answer('Введите количество этажей в доме')

@router.message(House.number_of_floors)
async def handle_number_of_floors_req_floor(message: Message, state: FSMContext):
    await state.update_data(number_of_floors=message.text)
    await state.set_state(House.floor)
    await message.answer('Введите желаемый этаж')

@router.message(House.floor)
async def handle_floor_req_apartment_type(message: Message, state: FSMContext):
    await state.update_data(floor=message.text)
    await state.set_state(House.apartment_type)
    await message.answer('Введите желаемый тип квартиры: Primary или Secondary')

@router.message(House.apartment_type)
async def handle_apartment_type_req_metro_station(message: Message, state: FSMContext):
    await state.update_data(apartment_type=message.text)
    await state.set_state(House.metro_station)
    await message.answer('Введите станцию метро поблизости')

@router.message(House.metro_station)
async def handle_metro_station_req_renovation(message: Message, state: FSMContext):
    await state.update_data(metro_station=message.text)
    await state.set_state(House.renovation)
    await message.answer('Введите ремонт: European-style renovation, Designer, Cosmetic или Without renovation')

@router.message(House.renovation)
async def handle_renovation_calculate_prediction(message: Message, state: FSMContext):
    await state.update_data(renovation=message.text)
    house_parameters = await state.get_data()
    price = predict_apartment_price(
        area=float(house_parameters.get('area')),
        number_of_rooms=int(house_parameters.get('number_of_rooms')),
        living_area=float(house_parameters.get('living_area')),
        kitchen_area=float(house_parameters.get('kitchen_area')),
        minutes_to_metro=int(house_parameters.get('minutes_to_metro')),
        number_of_floors=int(house_parameters.get('number_of_floors')),
        floor=int(house_parameters.get('floor')),
        apartment_type=house_parameters.get('apartment_type'),
        metro_station=house_parameters.get('metro_station'),
        renovation=house_parameters.get('renovation')
    )
    await message.reply(f"Вероятная цена квартиры с заданными параметрами: {price['formatted_price']}", reply_markup=keyboard.main)
    await state.clear()



