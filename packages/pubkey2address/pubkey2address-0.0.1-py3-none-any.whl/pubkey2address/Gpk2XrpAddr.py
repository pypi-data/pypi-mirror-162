from xrpl.core.keypairs import derive_classic_address
from coincurve import PublicKey

class GPK2XRPADDRESS:
    '''

    '''
    def getSmXrpAddr(self, gr):
        '''
                  {
                     "jsonrpc": "2.0",
                     "id": 1,
                     "result": {
                         "groupId": "0x000000000000000000000000000000000000000000000041726965735f303034",
                         "status": "5",
                         "deposit": "14977548978465740700066756",
                         "depositWeight": "17991035478465740700066756",
                         "selectedCount": "21",
                         "memberCount": "22",
                         "whiteCount": "1",
                         "whiteCountAll": "11",
                         "startTime": "1615262400",
                         "endTime": "1617940800",
                         "registerTime": "1614569510",
                         "registerDuration": "520098",
                         "memberCountDesign": "21",
                         "threshold": "15",
                         "chain1": "2153201998",
                         "chain2": "2147483708",
                         "curve1": "1",
                         "curve2": "0",
                         "tickedCount": "0",
                         "minStakeIn": "10000000000000000000000",
                         "minDelegateIn": "100000000000000000000",
                         "minPartIn": "10000000000000000000000",
                         "crossIncoming": "30000000000000000000",
                         "gpk1": "0x0c440bf2b594bdf526cbbcaae75dcb5f93d1f9bdd2f234f853fe4acf5f0e2d6d0525ad07f29f86943bc7c356a80e08e7345b12bc9bf5eb10e9d787b478f5ebb3",
                         "gpk2": "0x273c3273c072f826f728f865d58ccd297b293b87045fd806973d2a4d82f220a072bc5240c7d5920e0ddfdb0e01aeba184de9ef8ae14f5748243d8fa58d28e136",
                         "delegateFee": "1000"
                     }
                 }
         '''
        if gr['result']['curve1'] == 0:
            xrp_pk = gr['result']['gpk1']
        else:
            xrp_pk = gr['result']['gpk2']
        raw_key = bytes.fromhex('04' + xrp_pk[2::])
        compress_pub = PublicKey(raw_key).format()
        return derive_classic_address(compress_pub.hex())


    def genXrpAddr(self, pk):
        raw_key = bytes.fromhex('04' + pk[2::])
        compress_pub = PublicKey(raw_key).format()
        return derive_classic_address(compress_pub.hex())

if __name__ == '__main__':
    gr = {"jsonrpc": "2.0", "id": 1, "result": {"groupId": "0x000000000000000000000000000000000000000000000041726965735f303035", "status": "5", "deposit": "24145614584290259359204040", "depositWeight": "27336289084290259359204040", "selectedCount": "25", "memberCount": "25", "whiteCount": "1", "whiteCountAll": "11", "startTime": "1617940800", "endTime": "1620532800", "registerTime": "1617255580", "registerDuration": "512427", "memberCountDesign": "25", "threshold": "17", "chain1": "2153201998", "chain2": "2147483708", "curve1": "1", "curve2": "0", "tickedCount": "0", "minStakeIn": "10000000000000000000000", "minDelegateIn": "100000000000000000000", "minPartIn": "10000000000000000000000", "crossIncoming": "10740000000000000000000", "gpk1": "0x0c440bf2b594bdf526cbbcaae75dcb5f93d1f9bdd2f234f853fe4acf5f0e2d6d0525ad07f29f86943bc7c356a80e08e7345b12bc9bf5eb10e9d787b478f5ebb3", "gpk2": "0x273c3273c072f826f728f865d58ccd297b293b87045fd806973d2a4d82f220a072bc5240c7d5920e0ddfdb0e01aeba184de9ef8ae14f5748243d8fa58d28e136", "delegateFee": "1000"}}
    print(GPK2XRPADDRESS().getSmXrpAddr(gr))
    # print(genXrpAddr("7251664a3372615355544b6b7a4e35624373425a4e425473733159776b36796f"))