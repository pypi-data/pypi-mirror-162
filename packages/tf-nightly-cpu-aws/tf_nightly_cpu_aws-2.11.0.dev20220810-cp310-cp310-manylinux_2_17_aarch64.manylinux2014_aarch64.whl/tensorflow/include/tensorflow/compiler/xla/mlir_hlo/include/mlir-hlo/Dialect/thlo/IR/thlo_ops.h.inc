/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* Op Declarations                                                            *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/

#if defined(GET_OP_CLASSES) || defined(GET_OP_FWD_DEFINES)
#undef GET_OP_FWD_DEFINES
namespace mlir {
namespace thlo {
class ConcatenateOp;
} // namespace thlo
} // namespace mlir
namespace mlir {
namespace thlo {
class DynamicBroadcastInDimOp;
} // namespace thlo
} // namespace mlir
namespace mlir {
namespace thlo {
class GatherOp;
} // namespace thlo
} // namespace mlir
namespace mlir {
namespace thlo {
class ScatterOp;
} // namespace thlo
} // namespace mlir
#endif

#ifdef GET_OP_CLASSES
#undef GET_OP_CLASSES


//===----------------------------------------------------------------------===//
// Local Utility Method Definitions
//===----------------------------------------------------------------------===//

namespace mlir {
namespace thlo {

//===----------------------------------------------------------------------===//
// ::mlir::thlo::ConcatenateOp declarations
//===----------------------------------------------------------------------===//

class ConcatenateOpAdaptor {
public:
  ConcatenateOpAdaptor(::mlir::ValueRange values, ::mlir::DictionaryAttr attrs = nullptr, ::mlir::RegionRange regions = {});

  ConcatenateOpAdaptor(ConcatenateOp op);

  ::mlir::ValueRange getOperands();
  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index);
  ::mlir::ValueRange getODSOperands(unsigned index);
  ::mlir::ValueRange operands();
  ::mlir::Value init();
  ::mlir::DictionaryAttr getAttributes();
  ::mlir::IntegerAttr dimensionAttr();
  uint64_t dimension();
  ::mlir::LogicalResult verify(::mlir::Location loc);
private:
  ::mlir::ValueRange odsOperands;
  ::mlir::DictionaryAttr odsAttrs;
  ::mlir::RegionRange odsRegions;
  ::llvm::Optional<::mlir::OperationName> odsOpName;
};
class ConcatenateOp : public ::mlir::Op<ConcatenateOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::OneResult, ::mlir::OpTrait::OneTypedResult<::mlir::TensorType>::Impl, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::AtLeastNOperands<1>::Impl, ::mlir::OpTrait::OpInvariants, ::mlir::MemoryEffectOpInterface::Trait, ::mlir::OpTrait::SameOperandsAndResultElementType, ::mlir::gml_st::FusionInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = ConcatenateOpAdaptor;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("dimension")};
    return ::llvm::makeArrayRef(attrNames);
  }

  ::mlir::StringAttr dimensionAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr dimensionAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("thlo.concatenate");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index);
  ::mlir::Operation::operand_range getODSOperands(unsigned index);
  ::mlir::Operation::operand_range operands();
  ::mlir::Value init();
  ::mlir::MutableOperandRange operandsMutable();
  ::mlir::MutableOperandRange initMutable();
  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index);
  ::mlir::Operation::result_range getODSResults(unsigned index);
  ::mlir::Value result();
  ::mlir::IntegerAttr dimensionAttr();
  uint64_t dimension();
  void dimensionAttr(::mlir::IntegerAttr attr);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type result, ::mlir::ValueRange operands, ::mlir::Value init, ::mlir::IntegerAttr dimension);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::mlir::Value init, ::mlir::IntegerAttr dimension);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type result, ::mlir::ValueRange operands, ::mlir::Value init, uint64_t dimension);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::mlir::Value init, uint64_t dimension);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &p);
  ::mlir::LogicalResult verifyInvariantsImpl();
  ::mlir::LogicalResult verifyInvariants();
  ::mlir::LogicalResult verify();
  ::mlir::Value fuse(::mlir::Location loc, ::mlir::Value subset, OpBuilder&builder);
  void getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects);
private:
  ::mlir::StringAttr getAttributeNameForIndex(unsigned index) {
    return getAttributeNameForIndex((*this)->getName(), index);
  }

  static ::mlir::StringAttr getAttributeNameForIndex(::mlir::OperationName name, unsigned index) {
    assert(index < 1 && "invalid attribute index");
    return name.getRegisteredInfo()->getAttributeNames()[index];
  }

public:
  unsigned getNumInputs() {
    return this->getOperation()->getNumOperands() - getNumOutputs();
  };
  unsigned getNumOutputs() { return 1; };
};
} // namespace thlo
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::thlo::ConcatenateOp)

namespace mlir {
namespace thlo {

//===----------------------------------------------------------------------===//
// ::mlir::thlo::DynamicBroadcastInDimOp declarations
//===----------------------------------------------------------------------===//

class DynamicBroadcastInDimOpAdaptor {
public:
  DynamicBroadcastInDimOpAdaptor(::mlir::ValueRange values, ::mlir::DictionaryAttr attrs = nullptr, ::mlir::RegionRange regions = {});

  DynamicBroadcastInDimOpAdaptor(DynamicBroadcastInDimOp op);

  ::mlir::ValueRange getOperands();
  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index);
  ::mlir::ValueRange getODSOperands(unsigned index);
  ::mlir::Value operand();
  ::mlir::Value init();
  ::mlir::DictionaryAttr getAttributes();
  ::mlir::DenseI64ArrayAttr broadcast_dimensionsAttr();
  ::llvm::ArrayRef<int64_t> broadcast_dimensions();
  ::mlir::DenseI64ArrayAttr known_expanding_dimensionsAttr();
  ::llvm::Optional<::llvm::ArrayRef<int64_t>> known_expanding_dimensions();
  ::mlir::DenseI64ArrayAttr known_nonexpanding_dimensionsAttr();
  ::llvm::Optional<::llvm::ArrayRef<int64_t>> known_nonexpanding_dimensions();
  ::mlir::LogicalResult verify(::mlir::Location loc);
private:
  ::mlir::ValueRange odsOperands;
  ::mlir::DictionaryAttr odsAttrs;
  ::mlir::RegionRange odsRegions;
  ::llvm::Optional<::mlir::OperationName> odsOpName;
};
class DynamicBroadcastInDimOp : public ::mlir::Op<DynamicBroadcastInDimOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::VariadicResults, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::NOperands<2>::Impl, ::mlir::OpTrait::OpInvariants, ::mlir::MemoryEffectOpInterface::Trait, ::mlir::gml_st::FusionInterface::Trait, ::mlir::OpTrait::SameOperandsAndResultElementType> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = DynamicBroadcastInDimOpAdaptor;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("broadcast_dimensions"), ::llvm::StringRef("known_expanding_dimensions"), ::llvm::StringRef("known_nonexpanding_dimensions")};
    return ::llvm::makeArrayRef(attrNames);
  }

  ::mlir::StringAttr broadcast_dimensionsAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr broadcast_dimensionsAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  ::mlir::StringAttr known_expanding_dimensionsAttrName() {
    return getAttributeNameForIndex(1);
  }

  static ::mlir::StringAttr known_expanding_dimensionsAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 1);
  }

  ::mlir::StringAttr known_nonexpanding_dimensionsAttrName() {
    return getAttributeNameForIndex(2);
  }

  static ::mlir::StringAttr known_nonexpanding_dimensionsAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 2);
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("thlo.dynamic_broadcast_in_dim");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index);
  ::mlir::Operation::operand_range getODSOperands(unsigned index);
  ::mlir::Value operand();
  ::mlir::Value init();
  ::mlir::MutableOperandRange operandMutable();
  ::mlir::MutableOperandRange initMutable();
  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index);
  ::mlir::Operation::result_range getODSResults(unsigned index);
  ::mlir::Operation::result_range result();
  ::mlir::DenseI64ArrayAttr broadcast_dimensionsAttr();
  ::llvm::ArrayRef<int64_t> broadcast_dimensions();
  ::mlir::DenseI64ArrayAttr known_expanding_dimensionsAttr();
  ::llvm::Optional<::llvm::ArrayRef<int64_t>> known_expanding_dimensions();
  ::mlir::DenseI64ArrayAttr known_nonexpanding_dimensionsAttr();
  ::llvm::Optional<::llvm::ArrayRef<int64_t>> known_nonexpanding_dimensions();
  void broadcast_dimensionsAttr(::mlir::DenseI64ArrayAttr attr);
  void known_expanding_dimensionsAttr(::mlir::DenseI64ArrayAttr attr);
  void known_nonexpanding_dimensionsAttr(::mlir::DenseI64ArrayAttr attr);
  ::mlir::Attribute removeKnown_expanding_dimensionsAttr();
  ::mlir::Attribute removeKnown_nonexpanding_dimensionsAttr();
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange result, ::mlir::Value operand, ::mlir::Value init, ::mlir::DenseI64ArrayAttr broadcast_dimensions, /*optional*/::mlir::DenseI64ArrayAttr known_expanding_dimensions, /*optional*/::mlir::DenseI64ArrayAttr known_nonexpanding_dimensions);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &p);
  ::mlir::LogicalResult verifyInvariantsImpl();
  ::mlir::LogicalResult verifyInvariants();
  ::mlir::LogicalResult verify();
  ::mlir::Value fuse(::mlir::Location loc, ::mlir::Value subset, OpBuilder&builder);
  void getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects);
private:
  ::mlir::StringAttr getAttributeNameForIndex(unsigned index) {
    return getAttributeNameForIndex((*this)->getName(), index);
  }

  static ::mlir::StringAttr getAttributeNameForIndex(::mlir::OperationName name, unsigned index) {
    assert(index < 3 && "invalid attribute index");
    return name.getRegisteredInfo()->getAttributeNames()[index];
  }

public:
  unsigned getNumInputs() {
    return this->getOperation()->getNumOperands() - getNumOutputs();
  };
  unsigned getNumOutputs() { return 1; };
};
} // namespace thlo
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::thlo::DynamicBroadcastInDimOp)

namespace mlir {
namespace thlo {

//===----------------------------------------------------------------------===//
// ::mlir::thlo::GatherOp declarations
//===----------------------------------------------------------------------===//

class GatherOpAdaptor {
public:
  GatherOpAdaptor(::mlir::ValueRange values, ::mlir::DictionaryAttr attrs = nullptr, ::mlir::RegionRange regions = {});

  GatherOpAdaptor(GatherOp op);

  ::mlir::ValueRange getOperands();
  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index);
  ::mlir::ValueRange getODSOperands(unsigned index);
  ::mlir::Value operand();
  ::mlir::Value start_indices();
  ::mlir::Value init();
  ::mlir::DictionaryAttr getAttributes();
  ::mlir::LogicalResult verify(::mlir::Location loc);
private:
  ::mlir::ValueRange odsOperands;
  ::mlir::DictionaryAttr odsAttrs;
  ::mlir::RegionRange odsRegions;
  ::llvm::Optional<::mlir::OperationName> odsOpName;
};
class GatherOp : public ::mlir::Op<GatherOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::VariadicResults, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::NOperands<3>::Impl, ::mlir::OpTrait::OpInvariants, ::mlir::MemoryEffectOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = GatherOpAdaptor;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    return {};
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("thlo.gather");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index);
  ::mlir::Operation::operand_range getODSOperands(unsigned index);
  ::mlir::Value operand();
  ::mlir::Value start_indices();
  ::mlir::Value init();
  ::mlir::MutableOperandRange operandMutable();
  ::mlir::MutableOperandRange start_indicesMutable();
  ::mlir::MutableOperandRange initMutable();
  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index);
  ::mlir::Operation::result_range getODSResults(unsigned index);
  ::mlir::Operation::result_range result();
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange result, ::mlir::Value operand, ::mlir::Value start_indices, ::mlir::Value init);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &p);
  ::mlir::LogicalResult verifyInvariantsImpl();
  ::mlir::LogicalResult verifyInvariants();
  ::mlir::LogicalResult verify();
  void getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects);
public:
  unsigned getNumInputs() {
    return this->getOperation()->getNumOperands() - getNumOutputs();
  };
  unsigned getNumOutputs() { return 1; };
};
} // namespace thlo
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::thlo::GatherOp)

namespace mlir {
namespace thlo {

//===----------------------------------------------------------------------===//
// ::mlir::thlo::ScatterOp declarations
//===----------------------------------------------------------------------===//

class ScatterOpAdaptor {
public:
  ScatterOpAdaptor(::mlir::ValueRange values, ::mlir::DictionaryAttr attrs = nullptr, ::mlir::RegionRange regions = {});

  ScatterOpAdaptor(ScatterOp op);

  ::mlir::ValueRange getOperands();
  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index);
  ::mlir::ValueRange getODSOperands(unsigned index);
  ::mlir::Value indices();
  ::mlir::Value updates();
  ::mlir::Value init();
  ::mlir::DictionaryAttr getAttributes();
  ::mlir::LogicalResult verify(::mlir::Location loc);
private:
  ::mlir::ValueRange odsOperands;
  ::mlir::DictionaryAttr odsAttrs;
  ::mlir::RegionRange odsRegions;
  ::llvm::Optional<::mlir::OperationName> odsOpName;
};
class ScatterOp : public ::mlir::Op<ScatterOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::VariadicResults, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::NOperands<3>::Impl, ::mlir::OpTrait::OpInvariants, ::mlir::MemoryEffectOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = ScatterOpAdaptor;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    return {};
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("thlo.scatter");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index);
  ::mlir::Operation::operand_range getODSOperands(unsigned index);
  ::mlir::Value indices();
  ::mlir::Value updates();
  ::mlir::Value init();
  ::mlir::MutableOperandRange indicesMutable();
  ::mlir::MutableOperandRange updatesMutable();
  ::mlir::MutableOperandRange initMutable();
  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index);
  ::mlir::Operation::result_range getODSResults(unsigned index);
  ::mlir::Operation::result_range result();
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange result, ::mlir::Value indices, ::mlir::Value updates, ::mlir::Value init);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &p);
  ::mlir::LogicalResult verifyInvariantsImpl();
  ::mlir::LogicalResult verifyInvariants();
  ::mlir::LogicalResult verify();
  void getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects);
public:
  unsigned getNumInputs() {
    return this->getOperation()->getNumOperands() - getNumOutputs();
  };
  unsigned getNumOutputs() { return 1; };
};
} // namespace thlo
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::thlo::ScatterOp)


#endif  // GET_OP_CLASSES

