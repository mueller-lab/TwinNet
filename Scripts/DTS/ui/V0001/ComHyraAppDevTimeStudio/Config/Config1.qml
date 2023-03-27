import QtQuick 2.3

ConfigBase
{
    id: root

    configName : "Config1"

    property string pngRoot: "/media/muenalan/share/GOR-robustness_embryogenesis/data/Acquifer/0089-210420-ACQUIFER-mezzo/PNGs"

    property string pngImageFormat : "-%1--PO01/embryos/-%1--PO01--%3/-%1--PO01--LO%2--CO6--%3.png"
}
