#pragma once
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>

#include <pcl/Vertices.h>
#include <pcl/PointIndices.h>
#include <pcl/point_types.h>
#include <pcl/point_cloud.h>
#include <pcl/segmentation/supervoxel_clustering.h>
//#include <pcl/visualization/common/common.h>

#include <Eigen/Geometry>

PYBIND11_MAKE_OPAQUE(pcl::shared_ptr<std::vector<int>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::PointCloud<pcl::PointXYZRGB>>);
PYBIND11_MAKE_OPAQUE(std::vector<int>);
PYBIND11_MAKE_OPAQUE(std::vector<float>);
PYBIND11_MAKE_OPAQUE(std::vector<uint8_t>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::PointIndices>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::Vertices>);
//PYBIND11_MAKE_OPAQUE(std::vector<pcl::visualization::Camera>);

PYBIND11_MAKE_OPAQUE(Eigen::VectorXf);
PYBIND11_MAKE_OPAQUE(Eigen::Quaternionf);

//all pcl point types
PYBIND11_MAKE_OPAQUE(std::vector<pcl::PointXYZ, Eigen::aligned_allocator<pcl::PointXYZ>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::PointCloud<pcl::PointXYZ>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::PointXYZI, Eigen::aligned_allocator<pcl::PointXYZI>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::PointXYZL, Eigen::aligned_allocator<pcl::PointXYZL>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::Label, Eigen::aligned_allocator<pcl::Label>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::PointXYZRGBA, Eigen::aligned_allocator<pcl::PointXYZRGBA>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::PointXYZRGB, Eigen::aligned_allocator<pcl::PointXYZRGB>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::PointXYZRGBL, Eigen::aligned_allocator<pcl::PointXYZRGBL>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::PointXYZHSV, Eigen::aligned_allocator<pcl::PointXYZHSV>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::PointXY, Eigen::aligned_allocator<pcl::PointXY>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::InterestPoint, Eigen::aligned_allocator<pcl::InterestPoint>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::Axis, Eigen::aligned_allocator<pcl::Axis>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::Normal, Eigen::aligned_allocator<pcl::Normal>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::PointNormal, Eigen::aligned_allocator<pcl::PointNormal>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::PointXYZRGBNormal, Eigen::aligned_allocator<pcl::PointXYZRGBNormal>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::PointXYZINormal, Eigen::aligned_allocator<pcl::PointXYZINormal>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::PointXYZLNormal, Eigen::aligned_allocator<pcl::PointXYZLNormal>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::PointWithRange, Eigen::aligned_allocator<pcl::PointWithRange>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::PointWithViewpoint, Eigen::aligned_allocator<pcl::PointWithViewpoint>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::MomentInvariants, Eigen::aligned_allocator<pcl::MomentInvariants>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::PrincipalRadiiRSD, Eigen::aligned_allocator<pcl::PrincipalRadiiRSD>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::Boundary, Eigen::aligned_allocator<pcl::Boundary>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::PrincipalCurvatures, Eigen::aligned_allocator<pcl::PrincipalCurvatures>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::PFHSignature125, Eigen::aligned_allocator<pcl::PFHSignature125>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::PFHRGBSignature250, Eigen::aligned_allocator<pcl::PFHRGBSignature250>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::PPFSignature, Eigen::aligned_allocator<pcl::PPFSignature>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::CPPFSignature, Eigen::aligned_allocator<pcl::CPPFSignature>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::PPFRGBSignature, Eigen::aligned_allocator<pcl::PPFRGBSignature>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::NormalBasedSignature12, Eigen::aligned_allocator<pcl::NormalBasedSignature12>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::FPFHSignature33, Eigen::aligned_allocator<pcl::FPFHSignature33>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::VFHSignature308, Eigen::aligned_allocator<pcl::VFHSignature308>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::ESFSignature640, Eigen::aligned_allocator<pcl::ESFSignature640>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::BRISKSignature512, Eigen::aligned_allocator<pcl::BRISKSignature512>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::Narf36, Eigen::aligned_allocator<pcl::Narf36>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::IntensityGradient, Eigen::aligned_allocator<pcl::IntensityGradient>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::PointWithScale, Eigen::aligned_allocator<pcl::PointWithScale>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::PointSurfel, Eigen::aligned_allocator<pcl::PointSurfel>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::ShapeContext1980, Eigen::aligned_allocator<pcl::ShapeContext1980>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::UniqueShapeContext1960, Eigen::aligned_allocator<pcl::UniqueShapeContext1960>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::SHOT352, Eigen::aligned_allocator<pcl::SHOT352>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::SHOT1344, Eigen::aligned_allocator<pcl::SHOT1344>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::PointUV, Eigen::aligned_allocator<pcl::PointUV>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::ReferenceFrame, Eigen::aligned_allocator<pcl::ReferenceFrame>>);
PYBIND11_MAKE_OPAQUE(std::vector<pcl::PointDEM, Eigen::aligned_allocator<pcl::PointDEM>>);
//PYBIND11_MAKE_OPAQUE(std::vector<pcl::GRSDSignature21>);  // Linking error

//Supervoxel
//PYBIND11_MAKE_OPAQUE(std::map<uint32_t, pcl::Supervoxel<pcl::PointXYZ>::Ptr>);
//PYBIND11_MAKE_OPAQUE(std::map<uint32_t, pcl::Supervoxel<pcl::PointXYZI>::Ptr>);
//PYBIND11_MAKE_OPAQUE(std::map<uint32_t, pcl::Supervoxel<pcl::PointXYZL>::Ptr>);
//PYBIND11_MAKE_OPAQUE(std::map<uint32_t, pcl::Supervoxel<pcl::PointXYZRGBA>::Ptr>);
//PYBIND11_MAKE_OPAQUE(std::map<uint32_t, pcl::Supervoxel<pcl::PointXYZRGB>::Ptr>);
//PYBIND11_MAKE_OPAQUE(std::map<uint32_t, pcl::Supervoxel<pcl::PointXYZRGBL>::Ptr>);
//PYBIND11_MAKE_OPAQUE(std::map<uint32_t, pcl::Supervoxel<pcl::PointXYZHSV>::Ptr>);
//PYBIND11_MAKE_OPAQUE(std::map<uint32_t, pcl::Supervoxel<pcl::InterestPoint>::Ptr>);
//PYBIND11_MAKE_OPAQUE(std::map<uint32_t, pcl::Supervoxel<pcl::PointNormal>::Ptr>);
//PYBIND11_MAKE_OPAQUE(std::map<uint32_t, pcl::Supervoxel<pcl::PointXYZRGBNormal>::Ptr>);
//PYBIND11_MAKE_OPAQUE(std::map<uint32_t, pcl::Supervoxel<pcl::PointXYZINormal>::Ptr>);
//PYBIND11_MAKE_OPAQUE(std::map<uint32_t, pcl::Supervoxel<pcl::PointXYZLNormal>::Ptr>);
//PYBIND11_MAKE_OPAQUE(std::map<uint32_t, pcl::Supervoxel<pcl::PointWithRange>::Ptr>);
//PYBIND11_MAKE_OPAQUE(std::map<uint32_t, pcl::Supervoxel<pcl::PointWithViewpoint>::Ptr>);
//PYBIND11_MAKE_OPAQUE(std::map<uint32_t, pcl::Supervoxel<pcl::PointWithScale>::Ptr>);
//PYBIND11_MAKE_OPAQUE(std::map<uint32_t, pcl::Supervoxel<pcl::PointSurfel>::Ptr>);
//PYBIND11_MAKE_OPAQUE(std::map<uint32_t, pcl::Supervoxel<pcl::PointDEM>::Ptr>);