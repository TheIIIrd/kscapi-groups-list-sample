# #!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import socket
import urllib3
from KlAkOAPI.AdmServer import KlAkAdmServer
from KlAkOAPI.HostGroup import KlAkHostGroup
from KlAkOAPI.ChunkAccessor import KlAkChunkAccessor
from KlAkOAPI.Params import KlAkParams, KlAkArray


def GetServer(server_address, server_port, username, password):
    """Connects to KSC server"""
    server_url = f"https://{server_address}:{server_port}"
    server = KlAkAdmServer.Create(server_url, username, password, verify=False)
    return server


def FindGroups(oHostGroup, server, sFilter):
    """Searches KSC groups that require search filter"""
    print('Searching groups that require filter "' + sFilter + '":')

    res = oHostGroup.FindGroups(
        sFilter,
        vecFieldsToReturn=["id", "name", "grp_full_name", "parentId", "level"],
        vecFieldsToOrder=[],
        pParams={},
        lMaxLifeTime=100,
    )

    print("Found " + str(res.RetVal()) + " groups:")
    strAccessor = res.OutPar("strAccessor")

    # chunkAccessor object allows iteration over search results
    oChunkAccessor = KlAkChunkAccessor(server)
    nItemsCount = oChunkAccessor.GetItemsCount(strAccessor).RetVal()
    nStart = 0
    nStep = 20000

    while nStart < nItemsCount:
        oChunk = oChunkAccessor.GetItemsChunk(strAccessor, nStart, nStep).OutPar(
            "pChunk"
        )

        for parGroup in oChunk["KLCSP_ITERATOR_ARRAY"]:
            print(parGroup["grp_full_name"])
        nStart += nStep


def PrintGroupsTree(arrGroups, nLevel):
    """Recursively prints KSC group structure."""
    for group in arrGroups:
        nId = group["id"]
        strName = group["name"]
        strIndention = "    "

        for i in range(nLevel):
            strIndention += "  "
        strIndention += "+-"
        print(strIndention, "Subgroup:", strName, ", id:", nId)

        if "groups" in group:
            subgroups = group["groups"]
            PrintGroupsTree(subgroups, nLevel + 1)


def EnumerateGroups(oHostGroup):
    """Prints KSC group structure."""
    print('Enumerating subgroups in root group "Managed devices":')

    # get id of root group ('Managed devices' group)
    nRootGroupID = oHostGroup.GroupIdGroups().RetVal()

    # get subgroups tree, containing all grandchildren tree with no limits
    arrSubgroups = oHostGroup.GetSubgroups(nRootGroupID, 0).RetVal()

    # print tree of subgroups
    if arrSubgroups == None or len(arrSubgroups) == 0:
        print("Root group is empty")
    else:
        PrintGroupsTree(KlAkArray(arrSubgroups), 0)


def ParseGroupId(oHostGroup, nId):
    """Analyzes all groups from 0 to nId."""
    lstGroups = []

    if nId >= 0:
        for i in range(nId):
            try:
                groupInfo = oHostGroup.GetGroupInfo(i).RetVal()
                print("#" * 32, f"[ GROUP ID {i} ]\n{groupInfo}")
                lstGroups.append(groupInfo["name"] if "name" in groupInfo else None)
            except:
                print("There is no group with id", i)

    print(f"List of groups found by parsing:\n{', '.join(lstGroups)}")
    return lstGroups


def main():
    server_address = "<ip_address>"
    server_port = 13299
    username = "<username>"
    password = "<password>"

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # connect to KSC server
    server = GetServer(server_address, server_port, username, password)
    oHostGroup = KlAkHostGroup(server)

    # Simple enumeration of numbers
    ParseGroupId(oHostGroup, 15)
    print()

    # Search all groups
    FindGroups(oHostGroup, server, "")
    print()

    # print group structure
    EnumerateGroups(oHostGroup)
    return 0


if __name__ == "__main__":
    main()
