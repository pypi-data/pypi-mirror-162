Result and friends: various subclassable classes for deferred delivery of values.

*Latest release 20220805*:
Result now subclasses cs.fsm.FSM.

A `Result` is the base class for several callable subclasses
which will receive values at a later point in time,
and can also be used standalone without subclassing.

A call to a `Result` will block until the value is received or the `Result` is cancelled,
which will raise an exception in the caller.
A `Result` may be called by multiple users, before or after the value has been delivered;
if the value has been delivered the caller returns with it immediately.
A `Result`'s state may be inspected (pending, running, ready, cancelled).
Callbacks can be registered via a `Result`'s .notify method.

An incomplete `Result` can be told to call a function to compute its value;
the function return will be stored as the value unless the function raises an exception,
in which case the exception information is recorded instead.
If an exception occurred, it will be reraised for any caller of the `Result`.

Trite example:

    R = Result(name="my demo")

Thread 1:

    # this blocks until the Result is ready
    value = R()
    print(value)
    # prints 3 once Thread 2 (below) assigns to it

Thread 2:

    R.result = 3

Thread 3:

    value = R()
    # returns immediately with 3

You can also collect multiple `Result`s in completion order using the `report()` function:

    Rs = [ ... list of Results of whatever type ... ]
    ...
    for R in report(Rs):
        x = R()     # collect result, will return immediately because
                    # the Result is complete
        print(x)    # print result

## Function `after(Rs, R, func, *a, **kw)`

After the completion of `Rs` call `func(*a,**kw)` and return
its result via `R`; return the `Result` object.

Parameters:
* `Rs`: an iterable of Results.
* `R`: a `Result` to collect to result of calling `func`.
  If `None`, one will be created.
* `func`, `a`, `kw`: a callable and its arguments.

## Function `bg(func, *a, **kw)`

Dispatch a `Thread` to run `func`, return a `Result` to collect its value.

Parameters:
* `_name`: optional name for the `Result`, passed to the initialiser
* `_extra`: optional extra data for the `Result`, passed to the initialiser

Other parameters are passed to `func`.

## Class `CancellationError(builtins.Exception, builtins.BaseException)`

Raised when accessing `result` or `exc_info` after cancellation.

## Class `OnDemandFunction(Result, cs.fsm.FSM)`

Wrap a callable, run it when required.

## Class `OnDemandResult(Result, cs.fsm.FSM)`

Wrap a callable, run it when required.

## Function `report(LFs)`

Generator which yields completed `Result`s.

This is a generator that yields `Result`s as they complete,
useful for waiting for a sequence of `Result`s
that may complete in an arbitrary order.

## Class `Result(cs.fsm.FSM)`

Base class for asynchronous collection of a result.
This is used to make `Result`, `OnDemandFunction`s, `LateFunction`s
and other objects with asynchronous termination.

In addition to the methods below, for each state value such
as `self.PENDING` there is a corresponding attribute `is_pending`
testing whether the `Result` is in that state.

*Method `Result.__init__(self, name=None, lock=None, result=None, state=None, extra=None)`*:
Base initialiser for `Result` objects and subclasses.

Parameter:
* `name`: optional parameter naming this object.
* `lock`: optional locking object, defaults to a new `threading.Lock`.
* `result`: if not `None`, prefill the `.result` property.
* `extra`: an optional mapping of extra information to
  associate with the `Result`, useful to provide context
  when collecting the result; the `Result` has a public
  attribute `.extra` which is an `AttrableMapping` to hold
  this information.

*Method `Result.__call__(self, *a, **kw)`*:
Call the `Result`: wait for it to be ready and then return or raise.

You can optionally supply a callable and arguments,
in which case `callable(*args,**kwargs)` will be called
via `Result.call` and the results applied to this `Result`.

*Method `Result.bg(self, func, *a, **kw)`*:
Submit a function to compute the result in a separate `Thread`,
returning the `Thread`.

This dispatches a `Thread` to run `self.run_func(func,*a,**kw)`
and as such the `Result` must be in "pending" state,
and transitions to "running".

*Method `Result.cancel(self)`*:
Cancel this function.
If `self.fsm_state` is `PENDING`` or `'CANCELLED'`, return `True`.
Otherwise return `False` (too late to cancel).

*Property `Result.cancelled`*:
Test whether this `Result` has been cancelled.
Obsolete: use `.is_cancelled`.

*Method `Result.empty(self)`*:
Analogue to `Queue.empty()`.

*Property `Result.exc_info`*:
The exception information from a completed `Result`.
This is not available before completion.

*Method `Result.get(self, default=None)`*:
Wait for readiness; return the result if `self.exc_info` is `None`,
otherwise `default`.

*Method `Result.join(self, *a, **kw)`*:
Calling the `.join()` method waits for the function to run to
completion and returns a tuple as for the `WorkerThreadPool`'s
`.dispatch()` return queue, a tuple of `(result,exc_info)`.

On completion the sequence `(result,None)` is returned.
If an exception occurred computing the result the sequence
`(None,exc_info)` is returned
where `exc_info` is a tuple of `(exc_type,exc_value,exc_traceback)`.
If the function was cancelled the sequence `(None,None)`
is returned.

*Method `Result.notify(self, notifier)`*:
After the function completes, call `notifier(self)`.

If the function has already completed this will happen immediately.
example: if you'd rather `self` got put on some Queue `Q`, supply `Q.put`.

*Property `Result.pending`*:
Whether the `Result` is pending.
Obsolete: use `.is_pending`.

*Method `Result.put(self, value)`*:
Store the value. `Queue`-like idiom.

*Method `Result.raise_(self, exc=None)`*:
Convenience wrapper for `self.exc_info` to store an exception result `exc`.
If `exc` is omitted or `None`, uses `sys.exc_info()`.

*Property `Result.ready`*:
True if `Result` state is `DONE` or `CANCLLED`..

*Property `Result.result`*:
The result.
This property is not available before completion.

*Method `Result.run_func(self, func, *a, **kw)`*:
Have the `Result` run `func(*a,**kw)` and store its return value as
`self.result`.
If `func` raises an exception, store it as `self.exc_info`.

*Property `Result.state`*:
The `FSM` state (obsolete).
Obsolete: use `.fsm_state`.

## Class `ResultSet(builtins.set)`

A `set` subclass containing `Result`s,
on which one may iterate as `Result`s complete.

*Method `ResultSet.__iter__(self)`*:
Iterating on a `ResultSet` yields `Result`s as they complete.

*Method `ResultSet.wait(self)`*:
Convenience function to wait for all the `Result`s.

# Release Log



*Release 20220805*:
Result now subclasses cs.fsm.FSM.

*Release 20220311*:
* Result: class local Seq instance.
* Result.call: thread safe runtime check of self.state==pending.
* New Task and @task decorator, prototype for rerunnable blocking chaining tasks scheme - very alpha.

*Release 20210420*:
Update dependencies, add docstring.

*Release 20210407*:
New ResultSet(set) class, with context manager and wait methods, and whose __iter__ iterates completed Results.

*Release 20210123*:
bg: accept optional _extra parameter for use by the Result.

*Release 20201102*:
Result: now .extra attribute for associated data and a new optional "extra" parameter in the initialiser.

*Release 20200521*:
* OnDemandResult: bugfixes and improvements.
* Result.bg: accept optional _name parameter to specify the Result.name.

*Release 20191007*:
* Simplify ResultState definition.
* Result.bg: use cs.threads.bg to dispatch the Thread.

*Release 20190522*:
* Result.__call__ now accepts an optional callable and args.
* Result.call: set the Result state to "running" before dispatching the function.
* Rename OnDemandFunction to OnDemandResult, keep old name around for compatibility.
* Result._complete: also permitted if state==cancelled.

*Release 20190309*:
Small bugfix.

*Release 20181231*:
* Result.call: report baser exceptions than BaseException.
* Drop _PendingFunction abstract class.

*Release 20181109.1*:
DISTINFO update.

*Release 20181109*:
* Derive CancellationError from Exception instead of RuntimeError, fix initialiser.
* Rename AsynchState to ResultState and make it an Enum.
* Make Results hashable and comparable for equality for use as mapping keys: equality is identity.
* New Result.collected attribute, set true if .result or .exc_info are accessed, logs an error if Result.__del__ is called when false, may be set true externally if a Result is not required.
* Drop `final` parameter; never used and supplanted by Result.notify.
* Result.join: return the .result and .exc_info properties in order to mark the Result as collected.
* Result: set .collected to True when a notifier has been called successfully.
* Bugfix Result.cancel: apply the new cancelled state.

*Release 20171231*:
* Bugfix Result.call to catch BaseException instead of Exception.
* New convenience function bg(func) to dispatch `func` in a separate Thread and return a Result to collect its value.

*Release 20171030.1*:
Fix module requirements specification.

*Release 20171030*:
New Result.bg(func, *a, **kw) method to dispatch function in separate Thread to compute the Result value.

*Release 20170903*:
rename cs.asynchron to cs.result
