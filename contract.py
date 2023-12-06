import beaker
import pyteal as pt
from beaker.lib import storage
from beaker.decorators import Authorize

class MyAppState:
    user_count = beaker.GlobalStateValue(pt.TealType.uint64, default=pt.Int(0))
    docs_issued = beaker.GlobalStateValue(
        pt.TealType.uint64, default=pt.Int(0))
    org_name = beaker.GlobalStateValue(
        pt.TealType.bytes, default=pt.Bytes('NFTfiers'), static=True)
    org_type = beaker.GlobalStateValue(
        pt.TealType.bytes, default=pt.Bytes('Education'), static=True)
    users = storage.BoxMapping(pt.abi.Address, pt.abi.DynamicBytes)


app = beaker.Application('NFTicated', state=MyAppState())


@app.create
def create():
    return app.initialize_global_state()


@app.external(authorize=Authorize.only(pt.Global.creator_address()))
def add_user(user_address: pt.abi.Address, rollno: pt.abi.String, name: pt.abi.String, branch: pt.abi.String, *, output: pt.abi.String) -> pt.Expr:
    sender = pt.Txn.sender()
    is_creator = pt.Global.creator_address() == sender
    times = pt.Global.latest_timestamp()
    times = pt.Itob(times)
    str=pt.ScratchVar(pt.TealType.bytes)
    
    return pt.If(
        is_creator,
        pt.Seq(str.store(pt.Concat(pt.Bytes('{"grad":{"isgrad":"0","gradts":"00000000"},"rollno":"'), rollno.get(), pt.Bytes('","name":"'), name.get(), pt.Bytes('","branch":"'), branch.get(), pt.Bytes('","join_timestamp":"'), times, pt.Bytes('","certificates":{"...":"..."}}'))),
               pt.If(pt.App.box_create(user_address.get(),pt.Int(1000)),pt.Seq(pt.App.box_put(user_address.get(),
            pt.Bytes('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')),
             pt.App.box_replace(user_address.get(),pt.Int(0),str.load()), app.state.user_count.increment(),output.set(pt.Bytes('User address added successfully'))),output.set(pt.Bytes('User Already Exists')))),
        output.set(pt.Bytes('Only the application creator can add users'))
    )


@app.external(authorize=Authorize.only(pt.Global.creator_address()))
def add_certificate(user_address: pt.abi.Address, cert: pt.abi.String,pos:pt.abi.Uint64, *, output: pt.abi.String):
    mains = pt.ScratchVar(pt.TealType.bytes)
    return pt.Seq(bc := pt.App.box_get(user_address.get()),
                  pt.If(bc.hasValue())
                  .Then(mains.store(bc.value()),pt.If(check_position(mains,pos,user_address)).Then(pt.App.box_replace(user_address.get(),pos.get(),pt.Concat(cert.get(),pt.Bytes(',"...":"..."}}'))),output.set(pt.Bytes("Certificate Added"))).Else(output.set(pt.Bytes("Substring Not Matched"))))
                  .Else(output.set(pt.Bytes("Box has No Value"))))
    
@app.external(authorize=Authorize.only(pt.Global.creator_address()))
def make_grad(user_address:pt.abi.Address,*,output:pt.abi.String):
    is_grad=pt.ScratchVar(pt.TealType.bytes)
    return pt.Seq(bc := pt.App.box_get(user_address.get()),
                  pt.If(bc.hasValue())
                  .Then(pt.Seq(is_grad.store(pt.Substring(bc.value(),pt.Int(19),pt.Int(20))),
                               pt.If(pt.Eq(is_grad.load(),pt.Bytes("0")),
                                     pt.Seq(pt.App.box_replace(user_address.get(),pt.Int(19),pt.Concat(pt.Bytes('1","gradts":"'),pt.Itob(pt.Global.latest_timestamp()))),output.set("Made this user Graduated")),
                                     output.set(pt.Bytes("User is Already Grad"))),
                               ))
                  .Else(output.set(pt.Bytes("Box has No Value"))))
    # pos = pt.ScratchVar(pt.TealType.uint64)
    # mains = pt.ScratchVar(pt.TealType.bytes)
    # subs = pt.ScratchVar(pt.TealType.bytes)
    # return pt.Seq(bc := pt.App.box_get(user_address.get()),
    #               pt.Assert(bc.hasValue()),
    #               subs.store(pt.Bytes('","certificates":{')),
    #               mains.store(bc.value()),
    #               pos.store(chech_position(mains, subs)),
    #               pt.Assert(pos.load()),
    #               pt.App.box_replace(user_address.get(),
    #                                  pos.load(), cert.get()),
    #               output.set(pt.Bytes("Certificate Added Successfully"))
    #               )


@app.external
def get_user(user_address: pt.abi.Address, *, output: pt.abi.DynamicBytes):
    return pt.Seq(
        contents := pt.App.box_get(user_address.get()),
        pt.Assert(contents.hasValue()),
        output.set(contents.value())
    )


@pt.Subroutine(pt.TealType.uint64)
def check_position(main_s: pt.ScratchVar, pos: pt.abi.Uint64,user_address:pt.abi.Address):
    
    res=pt.ScratchVar(pt.TealType.uint64)
    return pt.Seq(pt.If
                  (pt.Eq(pt.Substring(main_s.load(),pos.get(),pt.Add(pos.get(),pt.Len(pt.Bytes('"...":"..."}}'))))
                         ,pt.Bytes('"...":"..."}}')))
                  .Then(res.store(pt.Int(1)))
                  .Else(res.store(pt.Int(0))),
                  pt.Return(res.load()))
    # i = pt.ScratchVar(pt.TealType.uint64)
    # res = pt.ScratchVar(pt.TealType.uint64)
    
    # return pt.Seq(res.store(pt.Int(0)),pt.For(i.store(pt.Int(0)), pt.Le(pt.Add(pt.Len(sub_s.load()),i.load()), pt.Len(main_s.load())), i.store(pt.Add(i.load(), pt.Int(1))))
    #         .Do(
    #     pt.If(pt.Eq(pt.Substring(main_s.load(), i.load(), pt.Add(pt.Len(sub_s.load()),i.load())), sub_s.load())).Then(res.store(pt.Add(i.load(), pt.Len(sub_s.load()))))), 
    #     pt.Return(res.load())
    # )


# Rest of the code...
if __name__ == '__main__':
    spec = app.build()
    spec.export('artifacts')
