using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace External.Systems.ICS
{
    public enum GearState : byte
    {
        None = 0,
        UpLock = 1,
        Move = 2,
        DownLock = 3
    }

    public enum ControlModeState : byte
    {
        Off = 0,
        Approach = 1,
        Landing = 2,
        Rollout = 3,
        Taxi = 4,
        ManualTest = 5
    }

    public enum ReverseEngineType : byte
    {
        Off = 0,
        Arm = 1,
        Deploy = 2
    }

    /// <summary>
    /// Интерфейс входных сигналов для Системы Интеллектуального Управления (Intelligent Control System).
    /// </summary>
    public struct ICSInputs
    {
        /// <summary>
        /// Валидность файзы полёта
        /// </summary>
        public byte FlightPhaseValid { get; set; }
        /// <summary>
        /// Фаза полёта: GateDeparture 1,
        ///                 TaxiOut 2,
        ///                 InitTakeoff_belowV1 3,
        ///                 InitTakeoff_before_lift_off 4,
        ///                 InitClimb 5, Climb 6, Cruise 7,
        ///                 Descent 8, Approach_Above30m 9,
        ///                 ApproachAbove15m 10, Land_flatteringAndTouchdown 11,
        ///                 LandRun 12, TaxiIn 13, GateArrival 14
        /// </summary>
        public byte FlightPhase { get; set; }

        /// <summary>
        /// Geodetic latitude Valid.
        /// </summary>
        public byte LatitudeValid { get; set; }
        /// <summary>
        /// Geodetic latitude. (deg)
        /// </summary>
        public double Latitude { get; set; }

        /// <summary>
        /// Geodetic longitude Valid.
        /// </summary>
        public byte LongitudeValid { get; set; }
        /// <summary>
        /// Geodetic longitude. (deg)
        /// </summary>
        public double Longitude { get; set; }

        /// <summary>
        /// Radio Height Valid.
        /// </summary>
        public byte RadioAltitudeValid { get; set; }
        /// <summary>
        /// DRA (Digital Radio Altimeter) Height. (Ft - футы)
        /// </summary>
        public float RadioAltitude { get; set; }


        /// <summary>
        /// Валидность Барометрической/геометрической высоты MSL.
        /// </summary>
        public byte BaroAltitudeValid { get; set; }
        /// <summary>
        /// Барометрическая/геометрическая высота MSL. (Ft - футы)
        /// </summary>
        public float BaroAltitude { get; set; }

        /// <summary>
        /// Валидность приборной скорости
        /// </summary>
        public byte IndicatedAirspeedValid { get; set; }
        /// <summary>
        /// Приборная скорость (kt - 1 kt ≈ 0.514 м/с; kt - узлы)
        /// </summary>
        public float IndicatedAirspeed { get; set; }

        /// <summary>
        /// Валидность истинной скорости
        /// </summary>
        public byte TrueAirspeedValid { get; set; }
        /// <summary>
        /// Истинная скорость (kt - 1 kt ≈ 0.514 м/с; kt - узлы)
        /// </summary>
        public float TrueAirspeed { get; set; }

        /// <summary>
        /// Валидность путевой скорости
        /// </summary>
        public byte GroundSpeedValid { get; set; }
        /// <summary>
        /// Путевая скорость для пробега/руления и скоростного профиля. (kt - 1 kt ≈ 0.514 м/с; kt - узлы)
        /// </summary>
        public float GroundSpeed { get; set; }

        /// <summary>
        /// Валидность вертикальной скорости
        /// </summary>
        public byte VerticalSpeedValid { get; set; }
        /// <summary>
        /// Вертикальная скорость снижения/выравнивания. (ft/min - футы в минуту)
        /// </summary>
        public float VerticalSpeed { get; set; }

        /// <summary>
        /// Валидность угла тангажа
        /// </summary>
        public byte PitchAngleValid { get; set; }
        /// <summary>
        /// Угол Тангажа (deg)
        /// </summary>
        public float PitchAngle { get; set; }

        /// <summary>
        /// Валидность угла крена
        /// </summary>
        public byte RollAngleValid { get; set; }
        /// <summary>
        /// Угол крена (deg)
        /// </summary>
        public float RollAngle { get; set; }

        /// <summary>
        /// Валидность магнитного курса
        /// </summary>
        public byte MagneticHeadingValid { get; set; }
        /// <summary>
        /// курс самолёта относительно магнитного севера (deg)
        /// </summary>
        public float MagneticHeading { get; set; }

        /// <summary>
        /// Валидность истинного курса
        /// </summary>
        public byte TrueHeadingValid { get; set; }
        /// <summary>
        /// курс самолёта относительно истинного севера (deg)
        /// </summary>
        public float TrueHeading { get; set; }

        /// <summary>
        /// Валидность магнитного путевого угла
        /// </summary>
        public byte TrkAngleMagneticValid { get; set; }
        /// <summary>
        /// магнитный путевой угол - направление фактического движения самолёта
        /// относительно поверхности Земли, отсчитанное от магнитного севера. (deg)
        /// </summary>
        public float TrkAngleMagnetic { get; set; }

        /// <summary>
        /// Валидность истинного путевого угла
        /// </summary>
        public byte TrkAngleTrueValid { get; set; }
        /// <summary>
        /// истинный путевой угол - направление фактического движения самолёта
        /// относительно поверхности Земли, отсчитанное от истинного севера. (deg)
        /// </summary>
        public float TrkAngleTrue { get; set; }

        /// <summary>
        /// Валидность угловой скорости тангажа
        /// </summary>
        public byte BodyPitchRateValid { get; set; }
        /// <summary>
        /// Угловая скорость тангажа самолёта в связанной системе координат. (deg/s)
        /// </summary>
        public float BodyPitchRate { get; set; }

        /// <summary>
        /// Валидность угловой скорости крена
        /// </summary>
        public byte BodyRollRateValid { get; set; }
        /// <summary>
        /// Угловая скорость крена самолёта в связанной системе координат. (deg/s)
        /// </summary>
        public float BodyRollRate { get; set; }

        /// <summary>
        /// Валидность угловой скорости рысканья
        /// </summary>
        public byte BodyYawRateValid { get; set; }
        /// <summary>
        /// Угловая скорость рысканья самолёта в связанной системе координат. (deg/s)
        /// </summary>
        public float BodyYawRate { get; set; }

        /// <summary>
        /// Валидность ускорения по нормальной оси самолёта
        /// </summary>
        public byte BodyNormAccelValid { get; set; }
        /// <summary>
        /// Ускорение по нормальной оси самолёта в связанной системе координат (g)
        /// </summary>
        public float BodyNormAccel { get; set; }

        /// <summary>
        /// Валидность ускорения самолёта вдоль его продольной оси
        /// </summary>
        public byte BodyLongAccelValid { get; set; }
        /// <summary>
        /// Ускорение самолёта вдоль его продольной оси X в связанной системе координат. (g)
        /// </summary>
        public float BodyLongAccel { get; set; }

        /// <summary>
        /// Валидность боковое ускорение самолёта вдоль оси
        /// </summary>
        public byte BodyLatAccelValid { get; set; }
        /// <summary>
        /// Боковое ускорение самолёта вдоль оси Y в связанной системе координат (g)
        /// </summary>
        public float BodyLatAccel { get; set; }

        /// <summary>
        /// Валидность магнитного/истинного направление ВПП
        /// </summary>
        public byte RunwayHeadingValid { get; set; }
        /// <summary>
        /// Магнитное/истинное направление ВПП  (deg)
        /// </summary>
        public float RunwayHeading { get; set; }

        /// <summary>
        /// длина ВПП  (m)
        /// </summary>
        public float RunwayLength { get; set; }

        /// <summary>
        /// ширина ВПП  (m)
        /// </summary>
        public float RunwayWidth { get; set; }

        /// <summary>
        /// Боковое отклонение от оси ВПП при наличии маршрута руления (m)
        /// </summary>
        public float LateralDeviation { get; set; }

        /// <summary>
        /// Валидность отклонения по курсовому каналу ILS/LOC
        /// </summary>
        public byte LocDeviationValid { get; set; }
        /// <summary>
        /// Отклонение по курсовому каналу ILS/LOC  (ddm)
        /// </summary>
        public float LocDeviation { get; set; }

        /// <summary>
        /// Валидность отклонения по глиссадному каналу
        /// </summary>
        public byte GSDeviationValid { get; set; }
        /// <summary>
        /// Отклонение по глиссадному каналу. (ddm)
        /// </summary>
        public float GSDeviation { get; set; }

        /// <summary>
        /// Состояние носового шасси. (None = 0, UpLock = 1, Move = 2, DownLock = 3)
        /// </summary>
        public GearState NoseGearStatus { get; set; }

        /// <summary>
        /// Состояние левого шасси. (None = 0, UpLock = 1, Move = 2, DownLock = 3)
        /// </summary>
        public GearState LeftGearStatus { get; set; }

        /// <summary>
        /// Состояние правого шасси. (None = 0, UpLock = 1, Move = 2, DownLock = 3)
        /// </summary>
        public GearState RightGearStatus { get; set; }

        /// <summary>
        /// Обжатие носового шасси (то есть самолёт сел на полосу и перенес вес на колесо).
        /// </summary>
        public byte NoseGearWeightOnWheels { get; set; }

        /// <summary>
        /// Обжатие левого шасси.
        /// </summary>
        public byte LeftGearWeightOnWheels { get; set; }

        /// <summary>
        /// Обжатие правого шасси.
        /// </summary>
        public byte RightGearWeightOnWheels { get; set; }

        /// <summary>
        /// Фактический угол поворота носового колеса. (deg)
        /// </summary>
        public float NoseWheelAngle { get; set; }

        /// <summary>
        /// Фактический положение предкрылков. (deg)
        /// </summary>
        public float SlatsAngle { get; set; }

        /// <summary>
        /// Фактическое положение закрылков. (deg)
        /// </summary>
        public float FlapsAngle { get; set; }

        /// <summary>
        /// Фактическое положение стабилизатора. (deg)
        /// </summary>
        public float StabilizerAngle { get; set; }

        /// <summary>
        /// Фактическое положение левого руля высоты. (deg)
        /// </summary>
        public float ElevatorLeftAngle { get; set; }

        /// <summary>
        /// Фактическое положение правого руля высоты. (deg)
        /// </summary>
        public float ElevatorRightAngle { get; set; }

        /// <summary>
        /// Фактическое положение левого элерона. (deg)
        /// </summary>
        public float AileronLeftAngle { get; set; }

        /// <summary>
        /// Фактическое положение правого элерона. (deg)
        /// </summary>
        public float AileronRightAngle { get; set; }

        /// <summary>
        /// Фактическое положение руля направления. (deg)
        /// </summary>
        public float RudderAngle { get; set; }

        /// <summary>
        /// Фактическая тяга левого двигателя. (%, 100%=10047 RPM)
        /// </summary>
        public float EngLeftThrust { get; set; }

        /// <summary>
        /// Фактическая тяга правого двигателя. (%, 100%=10047 RPM)
        /// </summary>
        public float EngRigntThrust { get; set; }

        /// <summary>
        /// Фактическое положение левого РУД. (deg, min -26.5 deg, max 55.0)
        /// </summary>
        public float LeftThrottleAngle { get; set; }

        /// <summary>
        /// Фактическое положение правого РУД. (deg, min -26.5 deg, max 55.0)
        /// </summary>
        public float RightThrottleAngle { get; set; }

        /// <summary>
        /// Фактическое положение левой педали тормоза. (mm, 0 mm - 36.73 mm)
        /// </summary>
        public float LeftBrakePedal { get; set; }

        /// <summary>
        /// Фактическое положение правой педали тормоза. (mm, 0 mm - 36.73 mm)
        /// </summary>
        public float RightBrakePedal { get; set; }

        /// <summary>
        /// Фактическое положение первого левого интерцептора. (deg, min "0", max "-48")
        /// </summary>
        public float LeftSpoiler1 { get; set; }

        /// <summary>
        /// Фактическое положение второго левого интерцептора. (deg, min "0", max "-48")
        /// </summary>
        public float LeftSpoiler2 { get; set; }

        /// <summary>
        /// Фактическое положение третьего левого интерцептора. (deg, min "0", max "-48")
        /// </summary>
        public float LeftSpoiler3 { get; set; }

        /// <summary>
        /// Фактическое положение четвертого левого интерцептора. (deg, min "0", max "-48")
        /// </summary>
        public float LeftSpoiler4 { get; set; }

        /// <summary>
        /// Фактическое положение левого воздушного тормоза. (deg, min "0", max "-48")
        /// </summary>
        public float LeftAirBrake { get; set; }

        /// <summary>
        /// Фактическое положение первого правого интерцептора. (deg, min "0", max "-48")
        /// </summary>
        public float RightSpoiler1 { get; set; }

        /// <summary>
        /// Фактическое положение второго правого интерцептора. (deg, min "0", max "-48")
        /// </summary>
        public float RightSpoiler2 { get; set; }

        /// <summary>
        /// Фактическое положение третьего правого интерцептора. (deg, min "0", max "-48")
        /// </summary>
        public float RightSpoiler3 { get; set; }

        /// <summary>
        /// Фактическое положение четвертого правого интерцептора. (deg, min "0", max "-48")
        /// </summary>
        public float RightSpoiler4 { get; set; }

        /// <summary>
        /// Фактическое положение правого воздушного тормоза. (deg, min "0", max "-48")
        /// </summary>
        public float RightAirBrake { get; set; }

        /// <summary>
        /// Истинное направление ветра. (deg)
        /// </summary>
        public float WindDirectionTrue { get; set; }

        /// <summary>
        /// Скорость ветра. (kt)
        /// </summary>
        public float WindSpeed { get; set; }

        /// <summary>
        /// Видимость. (ft)
        /// </summary>
        public float Visibility { get; set; }

        /// <summary>
        /// Интенсивность осадков. (0...1)
        /// </summary>
        public float PrecipitationRatio { get; set; }

        /// <summary>
        /// Состояние ВПП. (DRY - 0, WET - 1, ICE - 2, FLOODED - 3, WET RUBBER - 4, SNOWE - 5, SLUSH - 6)
        /// </summary>
        public int RunwayCondition { get; set; }

        /// <summary>
        /// Температура на аэродроме (deg)
        /// </summary>
        public float AirfieldTemp  { get; set; }

        /// <summary>
        /// Отказ левого двигателя
        /// </summary>
        public byte FaultLeftEngine { get; set; }

        /// <summary>
        /// Отказ правого двигателя
        /// </summary>
        public byte FaultRightEngine { get; set; }

        /// <summary>
        /// Отказ реверса левого двигателя
        /// </summary>
        public byte FaultLeftEngineReverse { get; set; }

        /// <summary>
        /// Отказ реверса правого двигателя
        /// </summary>
        public byte FaultRightEngineReverse { get; set; }

        /// <summary>
        /// Отказ левого шасси (0 - все в порядке,
        ///                     1 - Сбой разблокировки левого шасси в верхнем положении,
        ///                     2 - Сбой блокировки левого шасси в верхнем положении,
        ///                     3 - Сбой разблокировки левого шасси в нижнем положении,
        ///                     4 - Сбой блокировки левого шасси в нижнем положении,
        ///                     5 - Сбой открытия левой створки шасси,
        ///                     6 - Сбой закрытия левой створки шасси)
        /// </summary>
        public int FaultLeftLandingGear { get; set; }

        /// <summary>
        /// Отказ правого шасси (0 - все в порядке,
        ///                     1 - Сбой разблокировки шасси в верхнем положении,
        ///                     2 - Сбой блокировки шасси в верхнем положении,
        ///                     3 - Сбой разблокировки шасси в нижнем положении,
        ///                     4 - Сбой блокировки шасси в нижнем положении,
        ///                     5 - Сбой открытия створки шасси,
        ///                     6 - Сбой закрытия створки шасси)
        /// </summary>
        public int FaultRightLandingGear { get; set; }

        /// <summary>
        /// Отказ переднего шасси (0 - все в порядке,
        ///                     1 - Сбой разблокировки шасси в верхнем положении,
        ///                     2 - Сбой блокировки шасси в верхнем положении,
        ///                     3 - Сбой разблокировки шасси в нижнем положении,
        ///                     4 - Сбой блокировки шасси в нижнем положении,
        ///                     5 - Сбой открытия створки шасси,
        ///                     6 - Сбой закрытия створки шасси)
        /// </summary>
        public int FaultNoseLandingGear { get; set; }

        /// <summary>
        /// Отказ левого стабилизатора
        /// </summary>
        public byte FaultLeftStab { get; set; }

        /// <summary>
        /// Отказ правого стабилизатора
        /// </summary>
        public byte FaultRightStab { get; set; }

        /// <summary>
        /// Отказ управления носовым колесом
        /// </summary>
        public byte FaultNWS { get; set; }
    }


    /// <summary>
    /// Интерфейс выходных сигналов для Системы Интеллектуального Управления (Intelligent Control System).
    /// </summary>
    public struct ICSOutputs
    {
        public int ControlValidMask { get; set; }
        public ControlModeState ControlMode {  get; set; }
        public float ElevatorCmd { get; set; }
        public float AileronCmd { get; set; }
        public float RudderCmd { get; set; }
        public float ThrottleLeftRate { get; set; }
        public float ThrottleRightRate { get; set; }
        public float ThrottleLeft { get; set; }
        public float ThrottleRight { get; set; }
        public float NoseWheelTillerCmd { get; set; }
        public float RudderPedalCmd { get; set; }
        public float BrakeLeftCmd { get; set; }
        public float BrakeRightCmd { get; set; }
        public float AirbrakeCmd { get; set; }
        public ReverseEngineType ReverseLeftCmd { get; set; }
        public ReverseEngineType ReverseRightCmd { get; set; }
        public byte ModeAIReady { get; set; }
        public byte ModeLocCapture { get; set; }
        public byte ModeLocTrack { get; set; }
        public byte ModeGSCapture { get; set; }
        public byte ModeGSTrack { get; set; }
        public byte ModeFlareArm { get; set; }
        public byte ModeFlare { get; set; }
        public byte ModeAlignArm { get; set; }
        public byte ModeAlign { get; set; }
        public byte ModeRolloutArm { get; set; }
        public byte ModeRollout { get; set; }
        public byte ModeTaxiArm { get; set; }
        public byte ModeTaxi { get; set; }
        public byte ModeSpeed { get; set; }
        public byte ModeThrust { get; set; }
        public UInt64 WarningFlags { get; set; }
        public float QualityLateralError { get; set; }
        public float QualityHeadingError { get; set; }
        public float QualitySpeedError { get; set; }
        /// <summary>
        /// Резерв в массив из 14 байт под расширение без изменения размера структуры.
        /// </summary>
        public byte[] reserved { get; set; }
    }
}
