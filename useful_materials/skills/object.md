[
    {
        "id": "skill_0_1",
        "name": "Усиленный удар",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "desc": "Наносит физ урон. Откат 10 сек.",
        "powerSkill": 55,
        "icon": "https://i.ibb.co/VYgcQTmt/skill-0-1.webp",
        "timeout": 10000,
        "needMp": 10
    },
    {
        "id": "skill_0_2",
        "name": "Магический ледяной шар",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "magic",
        "needTypeWeapon": "staff",
        "desc": "Наносит маг урон, доп урон от мастерства холода. Откат 12 сек.",
        "powerSkill": 80,
        "icon": "https://i.ibb.co/gbCRR2kx/skill-0-2.webp",
        "timeout": 12000,
        "needMp": 14
    },
    {
        "id": "skill_1",
        "name": "Разрывающий удар",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "axe",
        "desc": "Наносит физ урон по выбранной цели. Если надет плащ Головореза - есть шанс (20%) нанести травму, добавляет один уровень травмы. Макс уровень 3. Каждый уровень травмы снижает наносимый вами урон на 10% (максимум 30%). Травмы не проходят сами, нужно использовать спец. эликсиры или бафы. Откат 40 сек. Если надет плащ Варвара - есть шанс (20%) оглушить цель на 15 сек. Откат 30 сек. Требуется тип оружия - топор.",
        "powerSkill": 150,
        "icon": "https://i.ibb.co/MDWkVwz9/skill-1.webp",
        "timeout": 40000,
        "needMp": 25,
        "chanceEffect": 20,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_1"
        }
    },
    {
        "id": "skill_2",
        "name": "Удар в прыжке",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "axe",
        "desc": "Наносит физ урон. Накладывает 1 стак травмы с шансом в 50%. Откат 40 сек. Требуется тип оружия - топор",
        "powerSkill": 140,
        "icon": "https://i.ibb.co/VWpTJCdp/skill-2.webp",
        "timeout": 40000,
        "needMp": 25,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_2"
        }
    },
    {
        "id": "skill_3",
        "name": "Ядовитый меч",
        "type": "active",
        "typeAttack": "attack",
        "secondTypeDamage": "poison",
        "needTypeWeapon": "sword",
        "desc": "Наносит физ урон, наносит доп урон от мастерства яда. Откат 30 сек. Требуется тип оружия - меч",
        "powerSkill": 140,
        "icon": "https://i.ibb.co/KcvJH4kP/skill-3.webp",
        "timeout": 30000,
        "needMp": 20,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_3"
        }
    },
    {
        "id": "skill_4",
        "name": "Кровавая рана",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "sword",
        "desc": "Наносит физ урон, 100% вызывает кровотечение 1 уровня, максимум 3 уровня, длительность 90 сек. Каждый раз когда цель пытается атаковать - то будет получать доп урон (10% * уровень кровотечения, то есть макс 30%). Откат 35 сек.",
        "powerSkill": 120,
        "icon": "https://i.postimg.cc/2yhPs466/skill-4.webp",
        "timeout": 35000,
        "needMp": 25,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_4"
        }
    },
    {
        "id": "skill_5",
        "name": "Переливание",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "sword",
        "desc": "Наносит физ урон, если на цели есть кровотечение, то восстанавливает себе HP 36% от собственного недостающего HP. Избыток HP снова возвращается, как урон на цель. Откат 30 сек.",
        "powerSkill": 140,
        "icon": "https://i.ibb.co/B5Hy6DcK/skill-5.webp",
        "timeout": 30000,
        "needMp": 30,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_5"
        }
    },
    {
        "id": "skill_6",
        "name": "Клинок ярости",
        "type": "active",
        "typeAttack": "soloBuff",
        "needTypeWeapon": "sword",
        "desc": "Баф - впадает в ярость, увеличивая свой урон на 30 сек, но теряя возможность защищаться. Увеличивает физ урон на 30% на 30 сек, но снижает физ защиту на 40%. Откат 60 сек",
        "powerSkill": 0,
        "icon": "https://i.ibb.co/3mFg6G0b/skill-6.webp",
        "timeAction": 30000,
        "timeout": 60000,
        "bonus": [
            {
                "name": "physicalDamage",
                "value": 30,
                "isPercent": "Y"
            },
            {
                "name": "physicalDef",
                "value": -40,
                "isPercent": "Y"
            }
        ],
        "needMp": 30,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_6"
        }
    },
    {
        "id": "skill_7",
        "name": "Героическая стойкость",
        "type": "active",
        "typeAttack": "soloBuff",
        "desc": "Окутывает неуязвимым покровом. В течение 20 секунд тело и дух обретают несокрушимую защиту (увеличивает маг и физ защиту на 300%). Откат 4 мин.",
        "powerSkill": 0,
        "icon": "https://i.ibb.co/j9kZG2cx/skill-7.webp",
        "timeAction": 20000,
        "timeout": 240000,
        "bonus": [
            {
                "name": "magicDef",
                "value": 300,
                "isPercent": "Y"
            },
            {
                "name": "physicalDef",
                "value": 300,
                "isPercent": "Y"
            }
        ],
        "needMp": 20
    },
    {
        "id": "skill_13",
        "name": "Убийственный выстрел",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "bow",
        "desc": "Наносит физ урон цели. Если у противника меньше 25% здоровья наносит удвоенный урон. Откат 60 сек. Требуется тип оружия - лук",
        "powerSkill": 180,
        "icon": "https://i.ibb.co/7dKbk7CD/skill-13.webp",
        "timeout": 60000,
        "needMp": 30,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_13"
        }
    },
    {
        "id": "skill_14",
        "name": "Прицельный выстрел",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "bow",
        "desc": "Наносит физический урон. Имеет повышеный на 10% шанс крита по цели. Откат 35 сек. Требуется тип оружия - лук",
        "powerSkill": 160,
        "icon": "https://i.ibb.co/YTfPJHtD/skill-14.webp",
        "timeout": 35000,
        "needMp": 20,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_14"
        }
    },
    {
        "id": "skill_15",
        "name": "Залп",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "bow",
        "targetVariant": "mass",
        "desc": "Выпускает несколько стрел наносящих физ урон и поражающих до 3 целей. Откат 40 сек. Требуется тип оружия - лук",
        "powerSkill": 140,
        "icon": "https://i.ibb.co/HfL94jCW/skill-15.webp",
        "timeout": 40000,
        "needMp": 40,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_15"
        }
    },
    {
        "id": "skill_16",
        "name": "Метка смерти",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "bow",
        "desc": "Вешает на цель метку смерти на 30 сек. Увеличивает урон, наносимый отмеченным целям вашими выстрелами на 5%. Увеличивает дополнительный урон при критическом ударе способностей на 20%. Откат 60 сек. Требуется тип оружия - лук",
        "powerSkill": 0,
        "icon": "https://i.ibb.co/1tKvTT1k/skill-16.webp",
        "timeout": 60000,
        "needMp": 30,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_16"
        }
    },
    {
        "id": "skill_17",
        "name": "Разрвыная стрела",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "bow",
        "secondTypeDamage": "fire",
        "desc": "Разрывной выстрел поражает цель нанося физ урон и дополнительный урон от мастерства огня. Накладывает эффект детонация. Детонация - После попадания в цель заряд наносит урон еще 2 раза в размере 15% от первоначального урона. Откат 60 сек. Требуется тип оружия - лук",
        "powerSkill": 160,
        "icon": "https://i.ibb.co/SwyTXw8n/skill-17.webp",
        "timeout": 60000,
        "needMp": 25,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_17"
        }
    },
    {
        "id": "skill_18",
        "name": "Черная стрела",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "bow",
        "secondTypeDamage": "dark",
        "desc": "Поражает цель нанося физ урон, наносит дополнительный урон от мастерства тьмы, накладывает на цель темную метку на 15 сек. Темная метка - повышает весь наносимый вами урон по цели на 6%. Откат 45 сек. Требуется тип оружия - лук",
        "powerSkill": 180,
        "icon": "https://i.ibb.co/QFxKSXFv/skill-18.webp",
        "timeout": 45000,
        "needMp": 25,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_18"
        }
    },
    {
        "id": "skill_19",
        "name": "Ядовитая стрела",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "bow",
        "secondTypeDamage": "poison",
        "desc": "Наносит физ урон, наносит доп урон от мастерства яда. Накладывает 1 стак отравления на 30 секунд. Макс количество стаков 5. Отравление - при ударе по противнику вы наносите дополнительный урон ядом (в размере 5%  * на количество стаков). При повторном наложении отравления обновляет время его действия. Откат 18 сек. Требуется тип оружия - лук",
        "powerSkill": 100,
        "icon": "https://i.ibb.co/TqqxPPVq/skill-19.webp",
        "timeout": 18000,
        "needMp": 20,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_19"
        }
    },
    {
        "id": "skill_20",
        "name": "Мультивыстрел",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "bow",
        "desc": "Наносит физ урон. Обновляет время действия <b>активного</b> дебафа: отравления, обморожения, темной метки или детонации. Обновляет рандомно (и при условии, что рандомный дебаф еще активен). Также в зависимости от обновляемого дебафа активируется <b>дополнительный</b> эффект: если обновит отравление – моментально восстанавливает 25% здоровья от урона способности, если обновит обморожение - увеличит физ урон игрока на 20% на 15 секунд, если обновит темную метку – моментально восполняет 25% маны от урона способности, если обновит детонацию – с шансом в 20% оглушит врага на 15 секунд. Откат 60 сек. Требуется тип оружия - лук",
        "powerSkill": 180,
        "icon": "https://i.ibb.co/WWjzBDLF/skill-20.webp",
        "timeout": 60000,
        "needMp": 30,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_20"
        }
    },
    {
        "id": "skill_21",
        "name": "Камуфляж",
        "type": "active",
        "typeAttack": "soloBuff",
        "needTypeWeapon": "bow",
        "desc": "Вы сливаетесь с окружающей обстановкой, из-за чего по вам сложней попасть. Повышает шанс уклонения на 20% на 30 секунд. Откат 60 сек. Требуется тип оружия - лук",
        "powerSkill": 0,
        "icon": "https://i.ibb.co/DP8Mgt6d/skill-21.webp",
        "timeout": 60000,
        "timeAction": 30000,
        "bonus": [
            {
                "name": "evasion",
                "value": 20
            }
        ],
        "needMp": 30,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_21"
        }
    },
    {
        "id": "skill_22",
        "name": "Морозная стрела",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "bow",
        "secondTypeDamage": "frost",
        "desc": "Выстрел стрелой с морозным наконечником по цели наносящий физ. урон. Наносит доп урон от мастерства холода. При попадании в цель накладывает 1 стак обморожения на врага на 30 секунд. Макс стаков 5. Обморожение - снижает физ и маг урон врага на 5% за каждый стак. Откат 18 сек. Требуется тип оружия - лук",
        "powerSkill": 100,
        "icon": "https://i.ibb.co/CKLJPr97/skill-22.webp",
        "timeout": 18000,
        "needMp": 20,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_22"
        }
    },
    {
        "id": "skill_23",
        "name": "Выпад",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "lance",
        "desc": "Вы делаете выпад копьем нанося физический урон. Если на вас есть стаки фехтования урон усиливается на 5% за каждый стак. После удара поглощает все стаки. Откат 40 сек. Требуется тип оружия - копье",
        "powerSkill": 150,
        "icon": "https://i.ibb.co/FLyS3RW3/skill-23.webp",
        "timeout": 40000,
        "needMp": 25,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_23"
        }
    },
    {
        "id": "skill_24",
        "name": "Вертикальный удар",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "lance",
        "desc": "Вы делаете вертикальный удар снизу вверх, наносящий физический урон и подбрасывающий врага, после чего он получает штраф к меткости на 10%. Накладывает на игрока стак фехтования на 30 секунд, суммирующийся до 5 раз. Фехтование - усиливает урон следующего выпада на 5%. Откат 16 сек. Требуется тип оружия - копье",
        "powerSkill": 100,
        "icon": "https://i.ibb.co/0pR8BPfx/skill-24.webp",
        "timeout": 16000,
        "needMp": 20,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_24"
        }
    },
    {
        "id": "skill_25",
        "name": "Горизонтальный удар",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "lance",
        "desc": "Вы делаете горизонтальный удар удар справа налево, наносящий физический урон и опрокидывающий цель, после чего она получает штраф к уклонению на 20%. Накладывает на игрока 1 стак бафа фехтование на 30 секунд за каждого пораженного врага. Суммируется до 5 раз. Фехтование - усиливает урон следующего Выпада на 5%. Откат 25 сек. Требуется тип оружия - копье",
        "powerSkill": 110,
        "icon": "https://i.ibb.co/nMY01Vc3/skill-25.webp",
        "timeout": 25000,
        "needMp": 20,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_25"
        }
    },
    {
        "id": "skill_26",
        "name": "Серия ударов",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "lance",
        "desc": "Наносит физ урон. Если на вас есть стаки фехтования, вы поглощаете их и за каждый стак фехтования, cерия ударов поражает дополнительную цель. Если в бою одна цель, то все дополнительные удары будут нанесены ей, если целей больше чем одна - все дополнительные удары будут нанесены рандомно по целям. Откат 90 сек. Требуется тип оружия - копье",
        "powerSkill": 170,
        "icon": "https://i.ibb.co/VYq9VpzZ/skill-26.webp",
        "timeout": 90000,
        "needMp": 40,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_26"
        }
    },
    {
        "id": "skill_27",
        "name": "Теневая коса",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "lance",
        "secondTypeDamage": "dark",
        "desc": "Вы трансформируете ваше копье в косу и совершаете широкую атаку, наносит физ урон и поражает до 3 целей (таргет и цели которые рядом). Наносит доп урон от мастерства тьмы. Каждая пораженная цель теряет часть (10%) от своего недостающего здоровья и восполняет его вам. Откат 45 сек. Требуется тип оружия - копье",
        "powerSkill": 125,
        "icon": "https://i.ibb.co/BHh4k5pM/skill-27.webp",
        "timeout": 45000,
        "needMp": 30,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_27"
        }
    },
    {
        "id": "skill_28",
        "name": "Пронзание",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "lance",
        "secondTypeDamage": "dark",
        "desc": "Вы пронзаете противника и наносите физ урон. Наносит доп урон от мастерства тьмы. В зависимости от восполненного здоровья от Теневой косы, получаете прибавку к урону. Каждая еденица HP увеличивает урон на 0.5. Откат 45 сек. Требуется тип оружия - копье",
        "powerSkill": 125,
        "icon": "https://i.ibb.co/v4SyWhZ1/skill-28.webp",
        "timeout": 45000,
        "needMp": 30,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_28"
        }
    },
    {
        "id": "skill_29",
        "name": "Ледяные когти",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "lance",
        "secondTypeDamage": "frost",
        "desc": "Наносит физ урон. Наносит доп урон от мастерства холода. При попадании крадет 15% физ урона у жертвы на 30 сек, уменьшая ее физ атаку на 15%. Откат 45 сек. Требуется тип оружия - копье",
        "powerSkill": 120,
        "icon": "https://i.ibb.co/WvVzc3RJ/skill-29.webp",
        "timeout": 45000,
        "needMp": 25,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_29"
        }
    },
    {
        "id": "skill_30",
        "name": "Ледяные вороны",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "lance",
        "secondTypeDamage": "frost",
        "desc": "Вы призываете стаю ледяных воронов вам на подмогу, которая сразу же вступает в бой и наносит урон. Количество воронов (но не меньше 1) зависит от физ. атаки которую вы украли за счет Ледяных когтей. (1 доп ворон = 50 физ. атаки украденной у противника). Вороны будут продолжать атаковать вашу цель вместе с вами в течении 30 секунд. Откат 70 сек. Требуется тип оружия - копье",
        "powerSkill": 120,
        "icon": "https://i.ibb.co/RZ0Crk1/skill-30.webp",
        "timeout": 70000,
        "needMp": 40,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_30"
        }
    },
    {
        "id": "skill_31",
        "name": "Ледяной защитник",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "lance",
        "secondTypeDamage": "frost",
        "desc": "Вы призываете ледяного медведя себе на подмогу, который сразу же вступает в бой и наносит урон. Здоровье и урон медведя зависит от физ урона который вы украли за счет Ледяных когтей. (100 хп за каждые 50 украденной физ атаки у противника). Медведь будет продолжать атаковать вашу цель вместе свами в течение 30 сек. Атаки медведя могут спровоцировать цель с шансом в 20%, заставив её переключить свое внимание на медведя и нанести медведю удар предназначавшийся игроку. Откат 70 сек. Требуется тип оружия - копье",
        "powerSkill": 120,
        "icon": "https://i.ibb.co/KcqGTBjQ/skill-31.webp",
        "timeout": 70000,
        "needMp": 40,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_31"
        }
    },
    {
        "id": "skill_32",
        "name": "Копье гарпун",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "lance",
        "desc": "Вы бросаете копье во врага приковывая его к месту и оглушая на 10 секунд. Откат 60 сек. Требуется тип оружия - копье",
        "powerSkill": 100,
        "icon": "https://i.ibb.co/35CtnVPV/skill-32.webp",
        "timeout": 60000,
        "needMp": 30,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_32"
        }
    },
    {
        "id": "skill_33",
        "name": "Укол",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "dager",
        "desc": "Наносит физ урон, накладывает 1 стак кровотечения (максимум 3 стака) длительностью 90 сек. Каждый раз когда цель пытается атаковать, то будет получать доп урон (10% * кол-во стаков кровотечения, то есть макс 30%). Откат 40 сек. Требуется тип оружия - кинжал",
        "powerSkill": 100,
        "icon": "https://i.ibb.co/JFGMCKjg/skill-33.webp",
        "timeout": 40000,
        "needMp": 25,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_33"
        }
    },
    {
        "id": "skill_34",
        "name": "Кровоизлияние",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "dager",
        "desc": "Наносит физ урон и усиливает эффекты кровотечения на цели на 25 секунд. Цель кровотечения вместо 10% доп урона за стак будет получать 15% доп урона за стак. Откат 40 сек. Требуется тип оружия - кинжал",
        "powerSkill": 110,
        "icon": "https://i.ibb.co/VcKbGPhC/skill-34.webp",
        "timeout": 40000,
        "needMp": 30,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_34"
        }
    },
    {
        "id": "skill_35",
        "name": "Отравляющий укол",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "secondTypeDamage": "poison",
        "needTypeWeapon": "dager",
        "desc": "Наносит физ урон. Наносит доп урон от мастерства яда и оставляет на цели 1 стак отравления на 30 секунд. Всего можно наложить 5 стаков. Отравление - при ударах по противнику вы наносите дополнительный урон ядом (в размере 5% * на количество стаков). При повторном наложении отравления обновляет время его действия (для всех стаков). Откат 15 сек. Требуется тип оружия - кинжал",
        "powerSkill": 80,
        "icon": "https://i.ibb.co/RGK3bzsh/skill-35.webp",
        "timeout": 15000,
        "needMp": 20,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_35"
        }
    },
    {
        "id": "skill_36",
        "name": "Расправа",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "secondTypeDamage": "poison",
        "needTypeWeapon": "dager",
        "desc": "Наносит физ урон. Наносит доп урон от мастерства яда. Целям, находящимся под воздействием отравления, наносится больше урона (5% * количество стаков). Откат 30 сек. Требуется тип оружия - кинжал",
        "powerSkill": 130,
        "icon": "https://i.ibb.co/21K2TmCC/skill-36.webp",
        "timeout": 30000,
        "needMp": 30,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_36"
        }
    },
    {
        "id": "skill_37",
        "name": "Кислотный удар",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "dager",
        "secondTypeDamage": "poison",
        "desc": "Наносит физ урон всем противникам (до 3 целей). Наносит доп урон от мастерства яда. Собирает (но не обнуляет) все стаки отравления с затронутых целей и за каждый стак отравления - получаете бонус к мастерству яда (на текущий удар) на 5% за стак. Откат 45 сек. Требуется тип оружия - кинжал",
        "powerSkill": 120,
        "icon": "https://i.ibb.co/LDXq11Dq/skill-37.webp",
        "timeout": 45000,
        "needMp": 40,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_37"
        }
    },
    {
        "id": "skill_38",
        "name": "Теневой удар",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "secondTypeDamage": "dark",
        "needTypeWeapon": "dager",
        "desc": "Наносит физ урон. Наносит доп урон от мастерства тьмы. После удара на игрока вешается баф <b>игра теней</b> на 45 сек. Игра теней - с шансом в 20% при атаках вы нанесете повторный удар на долю 20% от основного удара. Откат 60 сек. Требуется тип оружия - кинжал",
        "powerSkill": 120,
        "icon": "https://i.ibb.co/0pPYMGD1/skill-38.webp",
        "timeout": 60000,
        "needMp": 30,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_38"
        }
    },
    {
        "id": "skill_39",
        "name": "Погибель королей",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "secondTypeDamage": "dark",
        "needTypeWeapon": "dager",
        "desc": "Наносит физ урон. Наносит доп урон от мастерства тьмы. Если на игроке есть баф <b>игра теней</b> - получает удвоенный бонус от мастерства тьмы. Откат 60 сек. Требуется тип оружия - кинжал",
        "powerSkill": 150,
        "icon": "https://i.ibb.co/LLnhHGs/skill-39.webp",
        "timeout": 60000,
        "needMp": 30,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_39"
        }
    },
    {
        "id": "skill_40",
        "name": "Палач",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "secondTypeDamage": "dark",
        "needTypeWeapon": "dager",
        "desc": "Наносит физ урон. Наносит доп урон от мастерства тьмы. Если на вас действует баф <b>игра теней</b> - вы с вероятностью 10% убьете монстра (не действует на боссов), а игроку оставите 1% здоровья. Откат 60 сек. Требуется тип оружия - кинжал",
        "powerSkill": 160,
        "icon": "https://i.ibb.co/TqWnJC59/skill-40.webp",
        "timeout": 60000,
        "needMp": 30,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_40"
        }
    },
    {
        "id": "skill_41",
        "name": "Мясорубка",
        "type": "active",
        "typeAttack": "soloBuff",
        "needTypeWeapon": "dager",
        "desc": "Вы увеличиваете свой показатель физ урона на 20% на 30 секунд. Откат 60 сек. Требуется тип оружия - кинжал",
        "powerSkill": 0,
        "icon": "https://i.ibb.co/39kTkjxM/skill-41.webp",
        "timeout": 60000,
        "timeAction": 30000,
        "bonus": [
            {
                "name": "physicalDamage",
                "value": 20,
                "isPercent": "Y"
            }
        ],
        "needMp": 35,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_41"
        }
    },
    {
        "id": "skill_42",
        "name": "Заточка",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "dager",
        "desc": "Наносите небольшой физ урон. Развеивает все усиления (от боевых навыков) с противника и снижает физ и маг атаку противника на 20% на 30 секунд. Откат 90 сек. Требуется тип оружия - кинжал",
        "powerSkill": 50,
        "icon": "https://i.ibb.co/YF41m2HP/skill-42.webp",
        "timeout": 90000,
        "needMp": 35,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_42"
        }
    },
    {
        "id": "skill_43",
        "name": "Мощный удар",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "sword",
        "desc": "Наносит физ. урон. Пробивает броню противника, игнорируя 30% физ защиты цели. Откат 40 сек. Требуется тип оружия - меч",
        "powerSkill": 160,
        "icon": "https://i.ibb.co/4w7Ymch1/skill-43.webp",
        "timeout": 40000,
        "needMp": 40,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_43"
        }
    },
    {
        "id": "skill_44",
        "name": "Священный клинок",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "secondTypeDamage": "fire",
        "needTypeWeapon": "sword",
        "desc": "Наносит физ урон. Наносит доп урон от мастерства огня. Поражает противника священным клинком, раскалывая его душу на 2 части на 15 секунд. Пока душа врага расколота он наносит на 25% меньше урона. Если есть баф Суд богов, то наносит дополнительно накопленый урон. Откат 30 сек. Требуется тип оружия - меч",
        "powerSkill": 140,
        "icon": "https://i.ibb.co/gFFqW4v7/skill-44.webp",
        "timeout": 30000,
        "needMp": 40,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_44"
        }
    },
    {
        "id": "skill_45",
        "name": "Суд Богов",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "sword",
        "desc": "Вы вызываете противника на суд богов. В течение 25 сек весь урон нанесенный простыми ударами (удары с руки) накапливается и после завершения Суда богов, при использовании навыка Священный клинок вы нанесете весь накопленный урон. Откат 30 сек. Требуется тип оружия - меч",
        "powerSkill": 0,
        "icon": "https://i.ibb.co/cKVmS8Qz/skill-45.webp",
        "timeout": 30000,
        "needMp": 25,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_45"
        }
    },
    {
        "id": "skill_46",
        "name": "Опустошение",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "sword",
        "desc": "Наносит физ урон всем врагам (макс 3 цели) и имеет шанс в 50% наложить на них 1 стак кровотечения на 90 сек. Откат 40 сек. Требуется тип оружия - меч",
        "powerSkill": 120,
        "icon": "https://i.ibb.co/7t0ZTFr4/skill-46.webp",
        "timeout": 40000,
        "needMp": 35,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_46"
        }
    },
    {
        "id": "skill_47",
        "name": "Реванш",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "sword",
        "desc": "Наносит физ урон. Наносит дополнительный урон зависящий от последнего полученного урона персонажа (если был промах, то доп урон = 0). Откат 45 сек. Требуется тип оружия - меч",
        "powerSkill": 130,
        "icon": "https://i.ibb.co/wN9snbjb/skill-47.webp",
        "timeout": 45000,
        "needMp": 30,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_47"
        }
    },
    {
        "id": "skill_48",
        "name": "Волшебное оружие",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "sword",
        "desc": "Вы наделяете свое оружие силой огня на 30 секунд, каждая атака (включая с руки) будет наносить доп урон от мастерства огня противнику на величину равную части(5%) от вашей физ. атаки. Откат 90 сек. Требуется тип оружия - меч",
        "powerSkill": 0,
        "icon": "https://i.ibb.co/0j6PxjD6/skill-48.webp",
        "timeout": 90000,
        "needMp": 30,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_48"
        }
    },
    {
        "id": "skill_49",
        "name": "Казнь",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "axe",
        "desc": "Наносит физ. урон. Если на противнике есть эффект травмы, наносит дополнительный урон (в размере 10% * уровень травмы). Откат 40 сек. Требуется тип оружия - топор",
        "powerSkill": 130,
        "icon": "https://i.ibb.co/PZLgQns6/skill-49.webp",
        "timeout": 40000,
        "needMp": 25,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_49"
        }
    },
    {
        "id": "skill_50",
        "name": "Раскол брони",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "axe",
        "desc": "Удар наносящий слабый физ урон, повреждающий доспех противника и накладывающий эффект Раскол брони. Раскол брони - ослабляет броню противника на 4%, может суммироваться до 5 раз и действует 30 секунд. При повторном наложении обновляет время действия раскола брони. Откат 15 сек. Требуется тип оружия - топор",
        "powerSkill": 70,
        "icon": "https://i.ibb.co/DDL9V4ks/skill-50.webp",
        "timeout": 15000,
        "needMp": 20,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_50"
        }
    },
    {
        "id": "skill_51",
        "name": "Ледяная хватка",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "secondTypeDamage": "frost",
        "needTypeWeapon": "axe",
        "desc": "Наносит слабый физ урон. Наносит доп урон от мастерства холода. Имеет шанс в 30% нанести 1 уровень травмы. Откат 25 сек. Требуется тип оружия - топор",
        "powerSkill": 90,
        "icon": "https://i.ibb.co/01ksYfF/skill-51.webp",
        "timeout": 25000,
        "needMp": 20,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_51"
        }
    },
    {
        "id": "skill_52",
        "name": "Удар Левиафана",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "needTypeWeapon": "axe",
        "secondTypeDamage": "frost",
        "desc": "Вы окружаете свой топор ледяной коркой и обрушиваете его на врага нанося физ урон. Наносит дополнительный урон от мастерства холода. Если на противнике есть 3 уровня травмы, вы наносите повторный удар. Откат 50 сек. Требуется тип оружия - топор",
        "powerSkill": 180,
        "icon": "https://i.ibb.co/hJPXz110/skill-52.webp",
        "timeout": 50000,
        "needMp": 35,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_52"
        }
    },
    {
        "id": "skill_53",
        "name": "Яростные ветра",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "secondTypeDamage": "frost",
        "needTypeWeapon": "axe",
        "desc": "Вы начинаете кружиться в ледяном танце, нанося физ урон врагам. Наносит доп. урон от мастерства холода. За каждого задетого врага вы получаете 1 стак ярости на 20 секунд. Ярость - увеличивает критический урон на 5% за каждый стак. Откат 60 сек. Требуется тип оружия - топор",
        "powerSkill": 200,
        "icon": "https://i.ibb.co/sJ6S0wZQ/skill-53.webp",
        "timeout": 60000,
        "needMp": 40,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_53"
        }
    },
    {
        "id": "skill_54",
        "name": "Незатихающая буря",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "secondTypeDamage": "frost",
        "needTypeWeapon": "axe",
        "desc": "Удар наносящий повышенный физ урон если на вас есть стаки ярости, а на противнике есть стаки травмы. За каждый стак ярости урон от незатихающей бури увеличивается на 10%, за каждый стак травмы шанс критического урона незатихающей бури повышается на 5%. Откат 45 сек. Требуется тип оружия - топор",
        "powerSkill": 170,
        "icon": "https://i.ibb.co/GQJ26Ftr/skill-54.webp",
        "timeout": 45000,
        "needMp": 30,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_54"
        }
    },
    {
        "id": "skill_55",
        "name": "Буйство",
        "type": "active",
        "typeAttack": "soloBuff",
        "needTypeWeapon": "axe",
        "desc": "Повышает шанс критического урона игрока на 10% на 25 секунд. Откат 60 сек. Требуется тип оружия - топор",
        "powerSkill": 0,
        "icon": "https://i.ibb.co/rKdnxzx5/skill-55.webp",
        "timeout": 60000,
        "timeAction": 25000,
        "bonus": [
            {
                "name": "chanceCritical",
                "value": 10
            }
        ],
        "needMp": 30,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_55"
        }
    },
    {
        "id": "skill_56",
        "name": "Ледяной доспех",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "physical",
        "secondTypeDamage": "frost",
        "needTypeWeapon": "axe",
        "desc": "Покрывает броню ледяными шипами на 30 секунд. При атаках по врагу, вы выстреливаете этими шипами, нанося доп физ урон (20% от урона). Откат 60 сек. Требуется тип оружия - топор",
        "powerSkill": 0,
        "icon": "https://i.ibb.co/Vc9KQr1k/skill-56.webp",
        "timeout": 60000,
        "needMp": 30,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_56"
        }
    },
    {
        "id": "skill_8",
        "name": "Огненый шар",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "magic",
        "secondTypeDamage": "fire",
        "needTypeWeapon": "staff",
        "desc": "Пылающий шар сияет яркими оттенками пламени и мощно летит по воздуху, пока не врежется в свою цель с разрушительной силой. Наносит маг урон, доп урон от мастерства огня. Откат 20 сек.",
        "powerSkill": 150,
        "powerSkillEffect": 15,
        "icon": "https://i.ibb.co/FLZCRbYB/skill-8.webp",
        "timeout": 20000,
        "needMp": 30,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_8"
        }
    },
    {
        "id": "skill_57",
        "name": "Комета",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "magic",
        "secondTypeDamage": "fire",
        "needTypeWeapon": "staff",
        "desc": "Вы обрушиваете на врага огненную комету, наносящую маг урон (осколочный) всем противникам. Наносит доп урон от мастерства огня. При попадании комета поджигает область под собой и вешает дебаф горение на всех противников на 30 сек. Горение - наносит небольшой урон при атаках по цели в размере 5% от полученного урона. Откат 45 сек. Требуется тип оружия - маг (посох)",
        "powerSkill": 220,
        "icon": "https://i.ibb.co/4nv0chzV/skill-57.webp",
        "timeout": 45000,
        "needMp": 50,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_57"
        }
    },
    {
        "id": "skill_58",
        "name": "Огненный феникс",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "magic",
        "secondTypeDamage": "fire",
        "needTypeWeapon": "staff",
        "desc": "Вы призываете пламенного феникса который атакует цель нанося ей маг урон. Наносит доп урон от мастерства огня. Удар феникса наносит гарантированный критический урон. Откат 90 сек. Требуется тип оружия - маг (посох)",
        "powerSkill": 170,
        "icon": "https://i.ibb.co/rf2hwLGh/skill-58.webp",
        "timeout": 90000,
        "needMp": 35,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_58"
        }
    },
    {
        "id": "skill_59",
        "name": "Ожог",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "magic",
        "secondTypeDamage": "fire",
        "needTypeWeapon": "staff",
        "desc": "Наносит магический урон. Наносит доп урон от мастерства огня. Если здоровье противника ниже 30% - гарантированно наносит критический урон. Откат 30 сек. Требуется тип оружия - маг (посох)",
        "powerSkill": 160,
        "icon": "https://i.ibb.co/j9bBZc2r/skill-59.webp",
        "timeout": 30000,
        "needMp": 35,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_59"
        }
    },
    {
        "id": "skill_60",
        "name": "Искра",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "magic",
        "secondTypeDamage": "fire",
        "needTypeWeapon": "staff",
        "desc": "Вы помечаете цель огненной искрой на 15 сек, которая спустя время и под действием атак, взрывается нанося маг урон (цепной, то есть от большего к меньшему, чем дальше цель от таргета, тем меньше урона доходит) всем противникам. Наносит доп. урон от мастерства огня. Откат 30 сек. Требуется тип оружия - маг (посох)",
        "powerSkill": 160,
        "icon": "https://i.ibb.co/XryNdFzv/skill-60.webp",
        "timeout": 30000,
        "needMp": 35,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_60"
        }
    },
    {
        "id": "skill_9",
        "name": "Темная стая",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "magic",
        "secondTypeDamage": "dark",
        "needTypeWeapon": "staff",
        "desc": "Вырывается темная стая ворон, переполненная непроглядной магией и вечной жаждой крови. Наносит маг урон, доп урон от мастертсва тьмы. Откат 22 сек.",
        "powerSkill": 150,
        "icon": "https://i.ibb.co/b5qs5Vbp/skill-9.webp",
        "timeout": 22000,
        "needMp": 30,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_9"
        }
    },
    {
        "id": "skill_10",
        "name": "Кровавый жнец",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "magic",
        "secondTypeDamage": "dark",
        "needTypeWeapon": "staff",
        "desc": "Магия, пропитанная тьмой некромантии, наносит мощный удар, вырывая куски плоти из врагов и восстанавливая свое здоровье (20% от нанесенного урона). Откат 18 сек.",
        "powerSkill": 200,
        "icon": "https://i.ibb.co/kVpMPLSK/skill-10.webp",
        "timeout": 18000,
        "needMp": 35,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_10"
        }
    },
    {
        "id": "skill_61",
        "name": "Власть безумия",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "magic",
        "secondTypeDamage": "dark",
        "needTypeWeapon": "staff",
        "desc": "Наносит маг урон. Наносит доп. урон от мастерства тьмы. Создает теневого призрака на 20 секунд. Теневой призрак будет атаковать вместе с вами. Если перед этим заклинанием вы восстановили здоровье от навыка Кровавый жнец, то этот удар получает увеличенный урон на 20%. Откат 40 сек. Требуется тип оружия - маг (посох)",
        "powerSkill": 170,
        "icon": "https://i.ibb.co/8DMmkcyX/skill-61.webp",
        "timeout": 40000,
        "needMp": 40,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_61"
        }
    },
    {
        "id": "skill_62",
        "name": "Пожиратель разума",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "magic",
        "needTypeWeapon": "staff",
        "desc": "Создает под вашим контролем пожирателя разума сроком на 60 секунд. Пожиратель разума атакует вашу цель вместе с вами (если у вас изучен навык Темная стая - то использует его (40% его мощи) и наносит маг урон, в противном случае наносит физ урон, наследует статы хозяина в обои случаях). За каждый ваш удар - пожиратель разума крадёт с цели 5 едениц интеллектв (не работает против Боссов). Откат 90 сек. Требуется тип оружия - маг (посох)",
        "powerSkill": 0,
        "icon": "https://i.ibb.co/jvhx95jH/skill-62.webp",
        "timeout": 90000,
        "needMp": 50,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_62"
        }
    },
    {
        "id": "skill_63",
        "name": "Командир мертвых",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "magic",
        "secondTypeDamage": "dark",
        "needTypeWeapon": "staff",
        "desc": "Наносит маг урон. Наносит доп урон от мастерства тьмы. Если под вашим контролем находится Пожиратель разума, вы призываете Квалдира и Лича. Каждый из этих прислужников атакует врага вместе свами. Квалдир наносит урон основанный на вашей маг атаке. Лич наносит урон основанный на вашем мастерстве тьмы. Откат 90 сек. Требуется тип оружия - маг (посох)",
        "powerSkill": 220,
        "icon": "https://i.ibb.co/fLHYGxK/skill-63.webp",
        "timeout": 90000,
        "needMp": 50,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_63"
        }
    },
    {
        "id": "skill_11",
        "name": "Удар зевса",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "magic",
        "secondTypeDamage": "lightning",
        "needTypeWeapon": "staff",
        "desc": "Вызывает молнию и наносит точный удар по цели. Наносит маг урон, доп урон от мастерства молнии. Добавляет на цель +1 стак <b>заряжен<b/> на 30 сек. Откат 16 сек.",
        "powerSkill": 150,
        "icon": "https://i.ibb.co/nMkYbNgK/skill-11.webp",
        "timeout": 16000,
        "needMp": 30,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_11"
        }
    },
    {
        "id": "skill_64",
        "name": "Электрическое лассо",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "magic",
        "secondTypeDamage": "lightning",
        "needTypeWeapon": "staff",
        "desc": "Вы накидываете на противника электрическое лассо на 25 сек, цель получает доп урон когда её атакуют, а так же получает 1 стак дебафа <b>заряжен<b/> на 30 сек при каждой атаке. Макс количество стаков 5. <b>Заряжен</> - каждый стак понижает резист врага ко всем видам стихий на 5%. Откат 60 сек. Требуется тип оружия - маг (посох)",
        "powerSkill": 150,
        "icon": "https://i.ibb.co/hJ9V2sYV/skill-64.webp",
        "timeout": 60000,
        "needMp": 35,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_64"
        }
    },
    {
        "id": "skill_65",
        "name": "Шаровая молния",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "magic",
        "secondTypeDamage": "lightning",
        "needTypeWeapon": "staff",
        "desc": "Вы создаете шаровую молнию, которая движется к цели и при попадании поглощает все стаки дебафа <b>заряжен<b/> увеличивая свой урон на 5% за каждый стак. Откат 60 сек. Требуется тип оружия - маг (посох)",
        "powerSkill": 220,
        "icon": "https://i.ibb.co/p6NXJqtF/skill-65.webp",
        "timeout": 60000,
        "needMp": 40,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_65"
        }
    },
    {
        "id": "skill_66",
        "name": "Цепная молния",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "magic",
        "secondTypeDamage": "lightning",
        "needTypeWeapon": "staff",
        "desc": "Вы создаете цепной заряд молний поражающих всех противников цепным уроном (чем дальше от таргета, тем меньше урон), каждый пораженный противник получает 1 стак дебафа заряжен на 30 секунд. Откат 40 сек. Требуется тип оружия - маг (посох)",
        "powerSkill": 190,
        "icon": "https://i.ibb.co/dJV7cKrD/skill-66.webp",
        "timeout": 40000,
        "needMp": 50,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_66"
        }
    },
    {
        "id": "skill_67",
        "name": "Электрическая сеть",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "magic",
        "needTypeWeapon": "staff",
        "desc": "Вы заключаете противника в электрическую сеть, оглушая его. Время оглушения зависит от количества стаков <b>заряжен</b>. 1 стак = 3 сек. Поглощает все стаки дебафа <b>заряжен</>. Откат 40 сек. Требуется тип оружия - маг (посох)",
        "powerSkill": 0,
        "icon": "https://i.ibb.co/qMy9sLbb/skill-67.webp",
        "timeout": 40000,
        "needMp": 35,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_67"
        }
    },
    {
        "id": "skill_12",
        "name": "Стрела льда",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "magic",
        "secondTypeDamage": "frost",
        "needTypeWeapon": "staff",
        "desc": "Создает ледяную стрелу и наносит точный удар по цели. Наносит маг урон, доп урон от мастерства холода. Добавляет на цель 1 стак обморожения. Макс стаков 5. Откат 14 сек.",
        "powerSkill": 150,
        "icon": "https://i.ibb.co/7xxKsKfr/skill-12.webp",
        "timeout": 14000,
        "needMp": 30,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_12"
        }
    },
    {
        "id": "skill_68",
        "name": "Ледяное копье",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "magic",
        "secondTypeDamage": "frost",
        "needTypeWeapon": "staff",
        "desc": "Наносит небольшой маг урон. Наносит доп урон от мастерства холода. При попадании оставляет на враге 1 стак дебафа обморожение на 30 сек. Макс количество стаков 5. Обморожение - уменьшает физ и маг атаку врага на 5% за стак. Откат 12 сек. Требуется тип оружия - маг (посох)",
        "powerSkill": 100,
        "icon": "https://i.ibb.co/WN06XwSF/skill-68.webp",
        "timeout": 12000,
        "needMp": 25,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_68"
        }
    },
    {
        "id": "skill_69",
        "name": "Ледяной шторм",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "magic",
        "secondTypeDamage": "frost",
        "needTypeWeapon": "staff",
        "desc": "Вы взываете к силе льда, обрушивая на врага серию из 3 ледяных комет, наносящих маг урон, усиливается от мастерства холода. Если в бою несколько противников кометы летят в случайную цель. Если враг один все 3 кометы попадут в него. Каждое попадание кометы накладывает 1 стак обморожения, макс количество стаков 5. Обморожение - уменьшает физ и маг атаку врага на 5% за стак. Откат 70 сек. Требуется тип оружия - маг (посох)",
        "powerSkill": 180,
        "icon": "https://i.ibb.co/ycVyksdp/skill-69.webp",
        "timeout": 70000,
        "needMp": 40,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_69"
        }
    },
    {
        "id": "skill_70",
        "name": "Глубокая заморозка",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "magic",
        "secondTypeDamage": "frost",
        "needTypeWeapon": "staff",
        "desc": "Вы наносите небольшой маг урон и оглушаете врага. Время оглушения зависит от количества стаков обморожения на противнике. (1 стак = 3 сек). Поглощает все стаки обморожения с противника. Откат 60 сек. Требуется тип оружия - маг (посох)",
        "powerSkill": 100,
        "icon": "https://i.ibb.co/JjzTSgdY/skill-70.webp",
        "timeout": 60000,
        "needMp": 30,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_70"
        }
    },
    {
        "id": "skill_71",
        "name": "Раскалывание льда",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "magic",
        "secondTypeDamage": "frost",
        "needTypeWeapon": "staff",
        "desc": "Вы наносите большой магический урон. Наносит доп урон от магии холода. Каждый стак обморожения на противнике, увеличивает шанс крит удара на 5%. Откат 80 сек. Требуется тип оружия - маг (посох)",
        "powerSkill": 220,
        "icon": "https://i.ibb.co/pBK1M0Kt/skill-71.webp",
        "timeout": 80000,
        "needMp": 50,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_71"
        }
    },
    {
        "id": "skill_72",
        "name": "Колдовской поток",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "magic",
        "needTypeWeapon": "staff",
        "desc": "Вас окружает колдовская сила увеличивающая вашу маг атаку на случайную величину от 5% до 20% сроком на 25 секунд. Откат 60 сек. Требуется тип оружия - маг (посох)",
        "powerSkill": 0,
        "icon": "https://i.ibb.co/6Jm6vqLN/skill-72.webp",
        "timeout": 60000,
        "needMp": 30,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_72"
        }
    },
    {
        "id": "skill_73",
        "name": "Ледяной щит",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "magic",
        "needTypeWeapon": "staff",
        "desc": "Вы накладываете на себя щит на 30 секунд, который частично поглощающий физ. урон (25% от физ. атаки по вам) от 5 атак по вам. Откат 60 сек. Требуется тип оружия - маг (посох)",
        "powerSkill": 0,
        "icon": "https://i.ibb.co/RGT4fPMw/skill-73.webp",
        "timeout": 60000,
        "needMp": 30,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_73"
        }
    },
    {
        "id": "skill_74",
        "name": "Огненный щит",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "magic",
        "needTypeWeapon": "staff",
        "desc": "Вы накладываете на себя щит на 30 секунд, который частично поглощающий маг урон (25% от физ атаки) от 5 атак по вам. Откат 60 сек. Требуется тип оружия - маг (посох)",
        "powerSkill": 0,
        "icon": "https://i.ibb.co/ccmbq1jR/skill-74.webp",
        "timeout": 60000,
        "needMp": 30,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_74"
        }
    },
    {
        "id": "skill_75",
        "name": "Костяной щит",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "magic",
        "needTypeWeapon": "staff",
        "desc": "Вы призываете кости мертвых, которые окружают вас щитом на 30 секунд. Щит имеет 5 зарядов. При каждой атаке по вам, щит теряет 1 заряд и восстанавливает мам здоровье и ману в размере 5% от полученного урона. Откат 60 сек. Требуется тип оружия - маг (посох)",
        "powerSkill": 0,
        "icon": "https://i.ibb.co/Z1bVWgpS/skill-75.webp",
        "timeout": 60000,
        "needMp": 30,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_75"
        }
    },
    {
        "id": "skill_76",
        "name": "Щит молний",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "magic",
        "needTypeWeapon": "staff",
        "desc": "Вы призываете щит из молний, которые окружают вас на 30 секунд. Щит имеет 5 зарядов. При каждой свой атаке, щит теряет 1 заряд и наносит урон, основанный на полученом уроне. Откат 60 сек. Требуется тип оружия - маг (посох)",
        "powerSkill": 0,
        "icon": "https://i.ibb.co/rKpvbKTN/skill-76.webp",
        "timeout": 60000,
        "needMp": 30,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_76"
        }
    },
    {
        "id": "skill_77",
        "name": "Слабое исцеление",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "magic",
        "needTypeWeapon": "staff",
        "desc": "Исцеляет себя или выбранного члена пати. Работает от мудрости + маг урон. Откат 26 сек. Требуется тип оружия - маг (посох)",
        "powerSkill": 120,
        "icon": "https://i.ibb.co/k6J4hPSs/skill-77.webp",
        "timeout": 26000,
        "needMp": 25,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_77"
        }
    },
    {
        "id": "skill_78",
        "name": "Кокон жизни",
        "type": "active",
        "typeAttack": "attack",
        "typeDamage": "magic",
        "needTypeWeapon": "staff",
        "desc": "Вы окутываете союзника коконом жизни на 10 секунд, поглощающим урон в размере вашей маг. атаки и увеличивающий исцеление по союзнику на 25%. Откат 30 сек. Требуется тип оружия - маг (посох)",
        "powerSkill": 150,
        "icon": "https://i.ibb.co/V0J2jHCd/skill-78.webp",
        "timeout": 30000,
        "needMp": 35,
        "needLearn": {
            "skout": 100,
            "lvl": 1,
            "book": "book_skill_78"
        }
    }
]